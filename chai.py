'''
The chai test class.
'''

try:
  import unittest2
  unittest = unittest2
except ImportError:
  import unittest

from exception import *
from mock import Mock
from stub import stub
from collections import deque

class Chai(unittest.TestCase):
  '''
  Base class for all tests
  '''

  # mox uses a metaclass for wrapping setUp and tearDown, would be nice to
  # try and simplify if possible. For now expect

  def setUp(self):
    super(Chai,self).setUp()

    # Setup stub tracking
    self.stubs = deque()

  # Because cAmElCaSe sucks
  setup = setUp

  def tearDown(self):
    super(Chai,self).tearDown()

    # Docs insist that this will be called no matter what happens in runTest(),
    # so this should be a safe spot to unstub everything
    exception = None
    while len(self.stubs):
        stub = self.stubs.popleft()
        try:
          stub.assert_expectations()
        except ExpectationNotSatisfied, e:
          if not exception:
            exception = e

        stub.teardown() # Teardown the reset of the stub
      
    if exception: # Raise exception if not all expectations have been closed.
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
    if s not in self.stubs:
      self.stubs.append( s )
    return s

  def expect(self, obj, attr=None):
    '''
    Open and return an expectation on an object. Will automatically create a
    stub for the object. See stub documentation for argument information.
    '''
    return self.stub(obj,attr).expect()

  def mock(self):
    '''
    Return a mock object.
    '''
    return Mock()
