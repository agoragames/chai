'''
Implementation of stubbing
'''
from collections import deque
import inspect
import types

from expectation import Expectation
from exceptions import *

def stub(obj, attr=None):
  '''
  Stub an object. If attr is not None, will attempt to stub that attribute
  on the object. Only required for modules and other rare cases where we
  can't determine the binding from the object.
  '''
  if attr:
    return self._stub_attr(obj, attr)
  else:
    return self._stub_obj(obj)

def _stub_attr(obj, attr_name):
  '''
  Stub an attribute of an object. Will return an existing stub if there already
  is one.
  '''
  attr = getattr(obj, attr_name)
  
  # Return an existing stub
  if isinstance(attr, Stub):
    return attr

  if isinstance(attr, property):
    return StubProperty(obj, attr_name)

  if isinstance(attr, types.MethodType):
    return StubMethod(obj, attr_name)

  raise UnsupportedStub("can't stub %s of %s", attr_name, obj)


def _stub_obj(obj):
  '''
  Stub an object directly.
  '''
  # Return an existing stub
  if isinstance(obj, Stub):
    return obj
 
  # can't stub properties directly because  
  if isinstance(obj, property):
    return StubProperty(obj)

  


class Stub(object):
  '''
  Base class for all stubs.
  '''

  def __init__(self, obj, attr=None):
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
    self._expectations  = deque()

  def expect(self):
    '''
    Add an expectation to this stub. Return the expectation
    '''
    exp = Expectation()
    self._expectations.append( exp )
    return exp

  def __call__(self, *args, **kwargs):
    handled = False
    for exp in self._exepctations:
      handled = exp.call(*args, **kwargs)
      if handled: break

class StubProperty(Stub):
  '''
  Property stubbing.
  '''
  
  def __init__(self, obj, attr):
    super(Stub,self).__init__(obj, attr)
