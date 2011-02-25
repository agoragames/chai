'''
The chai test class.
'''

try:
  import unittest2
  unittest = unittest2
except ImportError:
  import unittest

from exceptions import *
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
    while len(self.stubs):
      stub = self.stubs.popleft()
      stub.assert_expectations()
      stub.teardown()

  # Because cAmElCaSe sucks
  teardown = tearDown


  def stub(obj, attr=None):
    '''
    Stub an object. If attr is not None, will attempt to stub that attribute
    on the object. Only required for modules and other rare cases where we
    can't determine the binding from the object.
    '''
    s = stub(obj, attr)
    self.stubs.append( s )
    return s

  def expect(obj, attr=None):
    '''
    Open and return an expectation on an object. Will automatically create a
    stub for the object. See stub documentation for argument information.
    '''
    self.stub(obj,attr).expect()
