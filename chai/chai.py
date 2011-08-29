'''
The chai test class.
'''

try:
  import unittest2
  unittest = unittest2
except ImportError:
  import unittest

import re
import sys
import inspect

from exception import *
from mock import Mock
from stub import stub
from collections import deque
from comparators import *


class ChaiTestType(type):
  """
  Metaclass used to wrap all test methods to make sure the assert_expectations
  in the correct context.
  """

  def __init__(cls, name, bases, d):
    type.__init__(cls, name, bases, d)

    # also get all the attributes from the base classes to account
    # for a case when test class is not the immediate child of MoxTestBase
    for base in bases:
      for attr_name in dir(base):
        d[attr_name] = getattr(base, attr_name)

    for func_name, func in d.items():
      if func_name.startswith('test') and callable(func):
        setattr(cls, func_name, ChaiTestType.test_wrapper(cls, func))

  @staticmethod
  def test_wrapper(cls, func):
    """
    Wraps a test method, when that test method has completed it 
    calls assert_expectations on the stub. This is to avoid getting to exceptions about the same error.
    """
    def wrapper(self, *args, **kwargs):
      func(self, *args, **kwargs)
      exceptions = []
      for stub in self._stubs:
        exceptions.extend(stub.unmet_expectations())
      
      if exceptions:
        raise ExpectationNotSatisfied(*exceptions)
      
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__
    return wrapper

class Chai(unittest.TestCase):
  '''
  Base class for all tests
  '''
  
  __metaclass__ = ChaiTestType

  # When initializing, alias all the cAmElCaSe methods to more helpful ones
  def __init__(self, *args, **kwargs):
    super(Chai,self).__init__(*args, **kwargs)
    for attr in dir(self):
      if attr.startswith('assert') and attr!='assert_':
        pieces = ['assert'] + re.findall('[A-Z][a-z]+', attr[5:])
        name = '_'.join( [s.lower() for s in pieces] )
        setattr(self, name, getattr(self,attr))

  # Load in the comparators
  equals = Equals
  almost_equals = AlmostEqual
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
    super(Chai,self).setUp()

    # Setup stub tracking
    self._stubs = deque()

    # Setup mock tracking
    self._mocks = deque()

    # Try to load this into the module that the test case is defined in, so
    # that 'self.' can be removed. This has to be done at the start of the test
    # because we need the reference to be correct at the time of test run, not
    # when the class is defined or an instance is created.
    mod = sys.modules[ self.__class__.__module__ ]
    for attr in dir(self):
      if attr.startswith('assert'):
        setattr(mod, attr, getattr(self, attr) )
      elif isinstance(getattr(self,attr), type) and issubclass( getattr(self,attr), Comparator ):
        setattr(mod, attr, getattr(self, attr) )
    setattr(mod, 'stub', self.stub)
    setattr(mod, 'expect', self.expect)
    setattr(mod, 'mock', self.mock)
    

  # Because cAmElCaSe sucks
  setup = setUp

  def tearDown(self):
    super(Chai,self).tearDown()

    # Docs insist that this will be called no matter what happens in runTest(),
    # so this should be a safe spot to unstub everything
    exception = None
    while len(self._stubs):
      stub = self._stubs.popleft()
      stub.teardown() # Teardown the reset of the stub
    
    # Do the mocks in reverse order in the rare case someone called mock(obj,attr)
    # twice.
    while len(self._mocks):
      mock = self._mocks.pop()
      if len(mock)==2:
        delattr( mock[0], mock[1] )
      else:
        setattr( mock[0], mock[1], mock[2] )

    # Clear out any cached variables
    Variable.clear()
    
    # Lastly, if there were any errors, raise them
    if exception:
      raise exception

  # Because cAmElCaSe sucks
  teardown = tearDown

  def stub(self, obj, attr=None):
    '''
    Stub an object. If attr is not None, will attempt to stub that attribute
    on the object. Only required for modules and other rare cases where we
    can't determine the binding from the object.
    '''
    s = stub(obj, attr)
    if s not in self._stubs:
      self._stubs.append( s )
    return s

  def expect(self, obj, attr=None):
    '''
    Open and return an expectation on an object. Will automatically create a
    stub for the object. See stub documentation for argument information.
    '''
    return self.stub(obj,attr).expect()

  def mock(self, obj=None, attr=None, **kwargs):
    '''
    Return a mock object.
    '''
    rval = Mock(**kwargs)
    if obj!=None and attr!=None:
      rval._object = obj
      rval._attr = attr
      
      if hasattr(obj,attr):
        orig = getattr(obj, attr)
        self._mocks.append( (obj,attr,orig) )
        setattr(obj, attr, rval)
      else:
        self._mocks.append( (obj,attr) )
        setattr(obj, attr, rval)
    return rval
