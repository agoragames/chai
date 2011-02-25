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
  return Stub(obj, attr)


class Stub(object):
  '''
  Base class for all stubs.
  '''

  def __init__(self, obj, attr):
    '''
    Setup the structs for expectations
    '''
    self._obj = obj
    self._attr = attr
    self._expectations = deque()
    self._is_met = True

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
    self._expectations = deque()

  def expect(self):
    '''
    Add an expectation to this stub. Return the expectation
    '''
    exp = Expectation(self)
    self._expectations.append( exp )
    return exp

  def __call__(self, *args, **kwargs):
    handled = False
    for exp in self._exepctations:
      res = exp.call(*args, **kwargs)
      if res.is_met:
        return res.return_value
      else:
        for rule in res.rules:
          # Use result to raise some kinda of error
          if rule.passed:
            # These passed
            pass
          else:
            # This failed
            pass
