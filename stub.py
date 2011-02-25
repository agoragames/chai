'''
Implementation of stubbing
'''
from collections import deque

from expectation import Expectation

def stub(obj, attr=None):
  '''
  Stub an object. If attr is not None, will attempt to stub that attribute
  on the object. Only required for modules and other rare cases where we
  can't determine the binding from the object.
  '''
  return Stub()


class Stub(object):
  '''
  Base class for all stubs.
  '''

  def __init__(self):
    '''
    Setup the structs for expectations
    '''
    self._expectations = deque()
    

  def assert_expectations(self):
    '''
    Assert that all expectations on the stub have been met.
    '''
    for exp in self._expectations:
      exp.is_met()

  def teardown(self):
    '''
    Clean up all expectations and restore the original attribute of the mocked
    object.
    '''
    self._expectations  = deque()

  def expect(self):
    '''
    Add an expectation to this stub. Return the expectation
    '''
    exp = Expectation()
    self._expectations.append( exp )
    return exp
