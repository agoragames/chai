'''
Copyright (c) 2011-2017, Agora Games, LLC All rights reserved.

https://github.com/agoragames/chai/blob/master/LICENSE.txt
'''
from __future__ import absolute_import

try:
    import unittest2
    unittest = unittest2
except ImportError:
    import unittest

import re
import sys
import inspect
import traceback
from collections import deque

from .exception import *
from .mock import Mock
from .stub import stub
from .comparators import *


class ChaiTestType(type):

    """
    Metaclass used to wrap all test methods to make sure the
    assert_expectations in the correct context.
    """

    def __init__(cls, name, bases, d):
        type.__init__(cls, name, bases, d)

        # also get all the attributes from the base classes to account
        # for a case when test class is not the immediate child of Chai
        # also alias all the cAmElCaSe methods to more helpful ones
        for base in bases:
            for attr_name in dir(base):
                d[attr_name] = getattr(base, attr_name)
                if attr_name.startswith('assert') and attr_name != 'assert_':
                    pieces = ['assert'] + \
                        re.findall('[A-Z][a-z]+', attr_name[5:])
                    name = '_'.join([s.lower() for s in pieces])
                    d[name] = getattr(base, attr_name)
                    setattr(cls, name, getattr(base, attr_name))

        for func_name, func in d.items():
            if func_name.startswith('test') and callable(func):
                setattr(cls, func_name, ChaiTestType.test_wrapper(cls, func))

    @staticmethod
    def test_wrapper(cls, func):
        """
        Wraps a test method, when that test method has completed it
        calls assert_expectations on the stub. This is to avoid getting to
        exceptions about the same error.
        """

        def wrapper(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
            except UnexpectedCall as e:
                # if this is not python3, use python2 syntax
                if not hasattr(e, '__traceback__'):
                    from .python2 import reraise
                    reraise(
                        AssertionError, '\n\n' + str(e), sys.exc_info()[-1])
                exc = AssertionError('\n\n' + str(e))
                setattr(exc, '__traceback__', sys.exc_info()[-1])
                raise exc
            finally:
                # Teardown all stubs so that if anyone stubbed methods that
                # would be called during exception handling (e.g. "open"),
                # the original method is used. Without, recursion limits are
                # common with little insight into what went wrong.
                exceptions = []
                try:
                    for s in self._stubs:
                        # Make sure we collect any unmet expectations before
                        # teardown.
                        exceptions.extend(s.unmet_expectations())
                        s.teardown()
                except:
                    # A rare case where this is about the best that can be
                    # done, as we don't want to supersede the actual
                    # exception if there is one.
                    traceback.print_exc()

            if exceptions:
                raise ExpectationNotSatisfied(*exceptions)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__module__ = func.__module__
        wrapper.__wrapped__ = func
        if getattr(func, '__unittest_skip__', False):
            wrapper.__unittest_skip__ = True
            wrapper.__unittest_skip_why__ = func.__unittest_skip_why__
        return wrapper


class ChaiBase(unittest.TestCase):
    '''
    Base class for all tests
    '''

    # Load in the comparators
    equals = Equals
    almost_equals = AlmostEqual
    length = Length
    is_a = IsA
    is_arg = Is
    any_of = Any
    all_of = All
    not_of = Not
    matches = Regex
    func = Function
    ignore_arg = Ignore
    ignore = Ignore
    in_arg = In
    contains = Contains
    var = Variable
    like = Like

    def setUp(self):
        super(ChaiBase, self).setUp()

        # Setup stub tracking
        self._stubs = deque()

        # Setup mock tracking
        self._mocks = deque()

        # Try to load this into the module that the test case is defined in, so
        # that 'self.' can be removed. This has to be done at the start of the
        # test because we need the reference to be correct at the time of test
        # run, not when the class is defined or an instance is created. Walks
        # through the method resolution order to set it on every module for
        # Chai subclasses to handle when tests are defined in subclasses.
        for cls in inspect.getmro(self.__class__):
            if cls.__module__.startswith('chai'):
                break
            mod = sys.modules[cls.__module__]
            for attr in dir(cls):
                if hasattr(mod, attr):
                    continue
                if attr.startswith('assert'):
                    setattr(mod, attr, getattr(self, attr))
                elif isinstance(getattr(self, attr), type) and \
                        issubclass(getattr(self, attr), Comparator):
                    setattr(mod, attr, getattr(self, attr))
            if not hasattr(mod, 'stub'):
                setattr(mod, 'stub', self.stub)
            if not hasattr(mod, 'expect'):
                setattr(mod, 'expect', self.expect)
            if not hasattr(mod, 'spy'):
                setattr(mod, 'spy', self.spy)
            if not hasattr(mod, 'mock'):
                setattr(mod, 'mock', self.mock)

    # Because cAmElCaSe sucks
    setup = setUp

    def tearDown(self):
        super(ChaiBase, self).tearDown()

        for cls in inspect.getmro(self.__class__):
            if cls.__module__.startswith('chai'):
                break
            mod = sys.modules[cls.__module__]

            if getattr(mod, 'stub', None) == self.stub:
                delattr(mod, 'stub')
            if getattr(mod, 'expect', None) == self.expect:
                delattr(mod, 'expect')
            if getattr(mod, 'spy', None) == self.spy:
                delattr(mod, 'spy')
            if getattr(mod, 'mock', None) == self.mock:
                delattr(mod, 'mock')

        # Docs insist that this will be called no matter what happens in
        # runTest(), so this should be a safe spot to unstub everything.
        # Even with teardown at the end of test_wrapper, tear down here in
        # case the test was skipped or there was otherwise a problem with
        # that test.
        while len(self._stubs):
            stub = self._stubs.popleft()
            stub.teardown()  # Teardown the reset of the stub

        # Do the mocks in reverse order in the rare case someone called
        # mock(obj,attr) twice.
        while len(self._mocks):
            mock = self._mocks.pop()
            if len(mock) == 2:
                delattr(mock[0], mock[1])
            else:
                setattr(mock[0], mock[1], mock[2])

        # Clear out any cached variables
        Variable.clear()

    # Because cAmElCaSe sucks
    teardown = tearDown

    def stub(self, obj, attr=None):
        '''
        Stub an object. If attr is not None, will attempt to stub that
        attribute on the object. Only required for modules and other rare
        cases where we can't determine the binding from the object.
        '''
        s = stub(obj, attr)
        if s not in self._stubs:
            self._stubs.append(s)
        return s

    def expect(self, obj, attr=None):
        '''
        Open and return an expectation on an object. Will automatically create
        a stub for the object. See stub documentation for argument information.
        '''
        return self.stub(obj, attr).expect()

    def spy(self, obj, attr=None):
        '''
        Open and return a spy on an object. Will automatically create a stub
        for the object. See stub documentation for argument information.
        '''
        return self.stub(obj, attr).spy()

    def mock(self, obj=None, attr=None, **kwargs):
        '''
        Return a mock object.
        '''
        rval = Mock(**kwargs)
        if obj is not None and attr is not None:
            rval._object = obj
            rval._attr = attr

            if hasattr(obj, attr):
                orig = getattr(obj, attr)
                self._mocks.append((obj, attr, orig))
                setattr(obj, attr, rval)
            else:
                self._mocks.append((obj, attr))
                setattr(obj, attr, rval)
        return rval


Chai = ChaiTestType('Chai', (ChaiBase,), {})
