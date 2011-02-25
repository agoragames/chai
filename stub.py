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
    return _stub_attr(obj, attr)
  else:
    return _stub_obj(obj)

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

  if isinstance(attr, type):
    return StubClass(attr)

  if isinstance(attr, types.MethodType):
    # Handle differently if unbound because it's an implicit "any instance"
    if attr.im_self==None:
      return StubUnboundMethod(attr)
    else:
      return StubMethod(attr)

  raise UnsupportedStub("can't stub %s of %s", attr_name, obj)


def _stub_obj(obj):
  '''
  Stub an object directly.
  '''
  # Return an existing stub
  if isinstance(obj, Stub):
    return obj
 
  # can't stub properties directly because the property object doesn't have
  # a reference to the class or name of the attribute on which it was defined
  if isinstance(obj, property):
    raise UnsupportedStub("must call stub(obj,attr) for properties")

  if isinstance(obj, type):
    return StubClass(obj)

  # I thought that types.UnboundMethodType differentiated these cases but
  # apparently not.
  if isinstance(obj, types.MethodType):
    # Handle differently if unbound because it's an implicit "any instance"
    if obj.im_self==None:
      return StubUnboundMethod(obj)
    else:
      return StubMethod(obj)

  raise UnsupportedStub("can't stub %s", obj)

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

class StubProperty(Stub):
  '''
  Property stubbing.
  '''
  
  def __init__(self, obj, attr):
    super(Stub,self).__init__(obj, attr)


class StubMethod(Stub):
  '''
  Stub a method.
  '''

  def __init__(self, obj):
    '''
    Initialize with an object of type MethodType
    '''
    super(StubMethod,self).__init__(obj)
    self._orig = obj
    self._instance = obj.im_self
    self._attr = obj.im_func.func_name

  def teardown(self):
    '''
    Replace the original method.
    '''
    setattr( self._instance, self._attr, self._orig )

class StubUnboundMethod(Stub):
  '''
  Stub an unbound method.
  '''

  def __init__(self, obj):
    '''
    Initialize with an object that is an unbound method
    '''
    super(StubUnboundMethod,self).__init__(obj)
    self._orig = obj
    self._instance = obj.im_class
    self._attr = obj.im_func.func_name

  def teardown(self):
    '''
    Replace the original method.
    '''
    setattr( self._instance, self._attr, self._orig )

class StubClass(Stub):
  '''
  Stub an actual class. Lots to do here like overriding attribute gets and
  so on.
  '''
