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
  # Annoying circular reference requires importing here. Would like to see
  # this cleaned up. @AW
  from mock import Mock

  attr = getattr(obj, attr_name)
  
  # Return an existing stub
  if isinstance(attr, Stub):
    return attr

  # If a Mock object, stub its __call__
  if isinstance(attr, Mock):
    return stub(attr.__call__)

  if isinstance(attr, property):
    return StubProperty(obj, attr_name)

  if isinstance(attr, types.MethodType):
    # Handle differently if unbound because it's an implicit "any instance"
    if attr.im_self==None:
      return StubUnboundMethod(attr)
    else:
      return StubMethod(obj, attr_name)

  # What an absurd type this is ....
  if type(attr).__name__ == 'method-wrapper':
    return StubMethodWrapper(attr)
  
  # This is also slot_descriptor
  if type(attr).__name__ == 'wrapper_descriptor':
    return StubWrapperDescriptor(obj, attr_name)

  raise UnsupportedStub("can't stub %s(%s) of %s", attr_name, type(attr), obj)


def _stub_obj(obj):
  '''
  Stub an object directly.
  '''
  # Annoying circular reference requires importing here. Would like to see
  # this cleaned up. @AW
  from mock import Mock

  # Return an existing stub
  if isinstance(obj, Stub):
    return obj

  # If a Mock object, stub its __call__
  if isinstance(obj, Mock):
    return stub(obj.__call__)
 
  # can't stub properties directly because the property object doesn't have
  # a reference to the class or name of the attribute on which it was defined
  if isinstance(obj, property):
    raise UnsupportedStub("must call stub(obj,attr) for properties")

  # I thought that types.UnboundMethodType differentiated these cases but
  # apparently not.
  if isinstance(obj, types.MethodType):
    # Handle differently if unbound because it's an implicit "any instance"
    if obj.im_self==None:
      return StubUnboundMethod(obj)
    else:
      return StubMethod(obj)

  # These aren't in the types library
  if type(obj).__name__ == 'method-wrapper':
    return StubMethodWrapper(obj)

  if type(obj).__name__ == 'wrapper_descriptor':
    raise UnsupportedStub("must call stub(obj,'%s') for slot wrapper on %s", 
      obj.__name__, obj.__objclass__.__name__ )
  
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
      if not exp.closed(with_counts=True):
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

  def __init__(self, obj, attr=None):
    '''
    Initialize with an object of type MethodType
    '''
    super(StubMethod,self).__init__(obj, attr)
    if not self._attr: 
      self._attr = obj.im_func.func_name
      self._instance = obj.im_self
    else:
      self._instance = self._obj
      self._obj = getattr( self._instance, self._attr )
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
  Stub a wrapper-descriptor. Only works when we can fetch it by name. Because
  the w-d object doesn't contain both the instance ref and the attribute name
  to be able to look it up. Used for mocking object.__init__ and related
  builtin methods when subclasses that don't overload those.
  '''

  def __init__(self, obj, attr_name):
    '''
    Initialize with an object that is a method wrapper.
    '''
    super(StubWrapperDescriptor,self).__init__(obj, attr_name)
    self._orig = getattr( self._obj, self._attr )
    setattr( self._obj, self._attr, self )

  def teardown(self):
    '''
    Replace the original method.
    '''
    setattr( self._obj, self._attr, self._orig )

