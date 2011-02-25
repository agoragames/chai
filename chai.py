'''
The chai test class.
'''

try:
  import unittest2
  unittest = unittest2
except ImportError:
  import unittest

from exceptions import *
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

    # Setup mock tracking
    self.mocks = deque()
    

  # Because cAmElCaSe sucks
  setup = setUp

  def tearDown(self):
    super(Chai,self).tearDown()

    # Docs insist that this will be called no matter what happens in runTest(),
    # so this should be a safe spot to unstub everything
    while len(self.stubs):
      stub = self.stubs.popleft()
      stub.assert_expectations()
      stub.teardown()

    # Do the mocks in reverse order in the rare case someone called mock(obj,attr)
    # twice.
    while len(self.mocks):
      mock = self.mocks.pop()
      if len(mock)==2:
        delattr( mock[0], mock[1] )
      else:
        setattr( mock[0], mock[1], mock[2] )

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

  def mock(self, obj=None, attr=None):
    '''
    Return a mock object.
    '''
    rval = Mock()
    if obj!=None and attr!=None:
      if hasattr(obj,attr):
        orig = getattr(obj, attr)
        self.mocks.append( (obj,attr,orig) )
        setattr(obj, attr, rval)
      else:
        self.mocks.append( (obj,attr) )
        setattr(obj, attr, rval)
    return rval
