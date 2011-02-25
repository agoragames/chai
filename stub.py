'''
Implementation of stubbing
'''
import inspect
import types

from expectation import Expectation
from exception import *

# For clarity here and in tests, could make these class or static methods on
# Stub. Chai base class would hide that.
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

  if isinstance(attr, type):
    return StubClass(attr)

  # What an absurd type this is ....
  if type(attr).__name__ == 'method-wrapper':
    return StubMethodWrapper(attr)

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

  if isinstance(obj, type):
    return StubClass(obj)

  # What an absurd type this is ....
  if type(obj).__name__ == 'method-wrapper':
    return StubMethodWrapper(obj)

  if type(obj).__name__ == 'wrapper_descriptor':
    return StubWrapperDescriptor(obj)

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
    self._expectations = []

  def assert_expectations(self):
    '''
    Assert that all expectations on the stub have been met.
    '''
    for exp in self._expectations:
      if not exp.closed():
        raise ExpectationNotSatisfied(exp)

  def teardown(self):
    '''
    Clean up all expectations and restore the original attribute of the mocked
    object.
    '''
    self._expectations = []

  def expect(self):
    '''
    Add an expectation to this stub. Return the expectation
    '''
    exp = Expectation(self)
    self._expectations.append( exp )
    return exp

  def __call__(self, *args, **kwargs):
    
    for exp in self._expectations:
      # If expectation closed skip
      if exp.closed():
        continue
      
      # If args don't match the expectation, close it and move on, else
      # pass to it for testing.
      if not exp.match(*args, **kwargs):
        exp.close(*args, **kwargs)
      else:
        return exp.test(*args, **kwargs)
    
    raise UnexpectedCall("No expectation in place for this call")

class StubProperty(Stub):
  '''
  Property stubbing.
  '''
  
  def __init__(self, obj, attr):
    super(StubProperty,self).__init__(obj, attr)
    setattr( self._obj, self._attr, self )


class StubMethod(Stub):
  '''
  Stub a method.
  '''

  def __init__(self, obj):
    '''
    Initialize with an object of type MethodType
    '''
    super(StubMethod,self).__init__(obj)
    self._instance = obj.im_self
    self._attr = obj.im_func.func_name
    setattr( self._instance, self._attr, self )

  def teardown(self):
    '''
    Replace the original method.
    '''
    setattr( self._instance, self._attr, self._obj )

class StubUnboundMethod(Stub):
  '''
  Stub an unbound method.
  '''

  def __init__(self, obj):
    '''
    Initialize with an object that is an unbound method
    '''
    super(StubUnboundMethod,self).__init__(obj)
    self._instance = obj.im_class
    self._attr = obj.im_func.func_name
    setattr( self._instance, self._attr, self )

  def teardown(self):
    '''
    Replace the original method.
    '''
    setattr( self._instance, self._attr, self._obj )

class StubMethodWrapper(Stub):
  '''
  Stub a method-wrapper.
  '''

  def __init__(self, obj):
    '''
    Initialize with an object that is a method wrapper.
    '''
    super(StubMethodWrapper,self).__init__(obj)
    self._instance = obj.__self__
    self._attr = obj.__name__
    setattr( self._instance, self._attr, self )

  def teardown(self):
    '''
    Replace the original method.
    '''
    setattr( self._instance, self._attr, self._obj )
    
class StubWrapperDescriptor(Stub):
  '''
  Stub a wrapper-descriptor. May never work because this might only be used
  for builtins that can't be overloaded.
  '''

  def __init__(self, obj):
    '''
    Initialize with an object that is a method wrapper.
    '''
    super(StubWrapperDescriptor,self).__init__(obj)
    self._instance = obj.__objclass__
    self._attr = obj.__name__
    setattr( self._instance, self._attr, self )

  def teardown(self):
    '''
    Replace the original method.
    '''
    setattr( self._instance, self._attr, self._obj )

class StubClass(Stub):
  '''
  Stub an actual class. Lots to do here like overriding attribute gets and
  so on.
  '''
