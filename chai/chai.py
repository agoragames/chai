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

class Chai(unittest.TestCase):
  '''
  Base class for all tests
  '''

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
  instance_of = InstanceOf
  is_a = InstanceOf
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
      try:
        stub.assert_expectations()
      except ExpectationNotSatisfied, e:
        if not exception: # Store only the first exception
          exception = e

      stub.teardown() # Teardown the reset of the stub
    
    # Do the mocks in reverse order in the rare case someone called mock(obj,attr)
    # twice.
    while len(self._mocks):
      mock = self._mocks.pop()
      if len(mock)==2:
        delattr( mock[0], mock[1] )
      else:
        setattr( mock[0], mock[1], mock[2] )
    
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

  def mock(self, obj=None, attr=None):
    '''
    Return a mock object.
    '''
    rval = Mock()
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
