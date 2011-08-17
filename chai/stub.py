'''
Implementation of stubbing
'''
import inspect
import types
import os
import sys
import gc

from expectation import Expectation, ArgumentsExpectationRule
from exception import *
from termcolor import colored

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

  # Check to see if this a property, this check is only for when dealing with an
  # instance. getattr will work for classes.
  is_property = False

  if not inspect.isclass(obj) and not inspect.ismodule(obj):
    attr = getattr(obj.__class__, attr_name)
    if isinstance(attr, property):
      is_property = True

  if not is_property:
    attr = getattr(obj, attr_name)

  # Return an existing stub
  if isinstance(attr, Stub):
    return attr

  # If a Mock object, stub its __call__
  if isinstance(attr, Mock):
    return stub(attr.__call__)

  if isinstance(attr, property):
    return StubProperty(obj, attr_name)

  # Sadly, builtin functions and methods have the same type, so we have to use
  # the same stub class even though it's a bit ugly
  if inspect.ismodule(obj) and \
  isinstance(attr, (types.FunctionType,types.BuiltinFunctionType,types.BuiltinMethodType)):
    return StubFunction(obj, attr_name)

  if isinstance(attr, types.MethodType):
    # Handle differently if unbound because it's an implicit "any instance"
    if attr.im_self==None:
      return StubUnboundMethod(attr)
    else:
      return StubMethod(obj, attr_name)

  if isinstance(attr, (types.BuiltinFunctionType,types.BuiltinMethodType)):
    return StubBuiltinFunction(attr)

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

  # (Mostly) Lastly, look for properties.
  # First look for the situation where there's a reference back to the property.
  prop = obj
  if isinstance( getattr( obj, '__self__', None), property ):
    obj = prop.__self__

  # Once we've found a property, we have to figure out how to reference back to
  # the owning class. This is a giant pain and we have to use gc to find out
  # where it comes from. This code is dense but resolves to something like this:
  # >>> gc.get_referrers( foo.x )
  # [{'__dict__': <attribute '__dict__' of 'foo' objects>,
  #   'x': <property object at 0x7f68c99a16d8>,
  #   '__module__': '__main__',
  #   '__weakref__': <attribute '__weakref__' of 'foo' objects>,
  #   '__doc__': None}]
  if isinstance(obj, property):
    klass,attr = None,None
    for ref in gc.get_referrers( obj ):
      if klass and attr: break
      if isinstance(ref,dict) and ref.get('prop',None) is obj :
        klass = getattr( ref.get('__dict__',None), '__objclass__', None )
        for name,val in getattr(klass,'__dict__',{}).iteritems():
          if val is obj:
            attr = name
            break

    if klass and attr:
      rval = stub(klass,attr)
      if prop != obj:
        return stub(rval, prop.__name__)
      return rval

  # If a function and it has an associated module, we can mock directly.
  # Note that this *must* be after properties, otherwise it conflicts with
  # stubbing out the deleter methods and such
  # Sadly, builtin functions and methods have the same type, so we have to use
  # the same stub class even though it's a bit ugly
  if isinstance(obj, (types.FunctionType,types.BuiltinFunctionType,types.BuiltinMethodType)) and hasattr(obj, '__module__'):
    return StubFunction(obj)

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

  @property
  def name(self):
    return None # The base class implement this.

  def unmet_expectations(self):
    '''
    Assert that all expectations on the stub have been met.
    '''
    unmet = []
    for exp in self._expectations:
      if not exp.closed(with_counts=True):
        unmet.append(ExpectationNotSatisfied(exp))
    return unmet

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

    raise UnexpectedCall("\n\n" + self._format_exception(ArgumentsExpectationRule.pretty_format_args(*args, **kwargs)))

  def _format_exception(self, args_str):
    result = [
      colored("No expectation in place for %s with %s" % (self.name, args_str), "red"),
      "All Expectations:"
    ]
    for exception in self._expectations:
      result.append(str(exception))

    return "\n".join(result)

class StubProperty(Stub, property):
  '''
  Property stubbing.
  '''

  def __init__(self, obj, attr):
    super(StubProperty,self).__init__(obj, attr)
    property.__init__(self, lambda x: self(),
      lambda x, val: self.setter(val), lambda x: self.deleter() )
    # In order to stub out a property we have ask the class for the propery object
    # that was created we python execute class code.
    if inspect.isclass(obj):
      self._instance = obj
    else:
      self._instance = obj.__class__

    # Use a simple Mock object for the deleter and setter. Use same namespace
    # as property type so that it simply works.
    # Annoying circular reference requires importing here. Would like to see
    # this cleaned up. @AW
    from mock import Mock
    self._obj = getattr(obj, attr)
    self.setter = Mock()
    self.deleter = Mock()

    setattr(self._instance, self._attr, self)

  @property
  def name(self):
    return "%s.%s" % (self._instance.__name__, self._attr)


  def teardown(self):
    '''
    Replace the original method.
    '''
    setattr( self._instance, self._attr, self._obj )

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

  @property
  def name(self):
    from mock import Mock # Import here for the same reason as above.
    if hasattr(self._obj, 'im_class'):
      if issubclass(self._obj.im_class, Mock):
        return "%s (on mock object)" % self._obj.im_self._name

    # Always use the class to get the name
    klass = self._instance
    if not inspect.isclass(self._instance):
      klass = self._instance.__class__

    return "%s.%s" % (klass.__name__, self._attr)

  def teardown(self):
    '''
    Put the original method back in place. This will also handle the special case
    when it putting back a class method.

    The following code snippet best describe why it fails using settar, the
    class method would be replaced with a bound method not a class method.

    >>> class Example(object):
    ...     @classmethod
    ...     def a_classmethod(self):
    ...         pass
    ...
    >>> Example.__dict__['a_classmethod'] # Note the classmethod is returned.
    <classmethod object at 0x7f5e6c298be8>
    >>> orig = getattr(Example, 'a_classmethod')
    >>> orig
    <bound method type.a_classmethod of <class '__main__.Example'>>
    >>> setattr(Example, 'a_classmethod', orig)
    >>> Example.__dict__['a_classmethod'] # Note that setattr set a bound method not a class method.
    <bound method type.a_classmethod of <class '__main__.Example'>>

    The only way to figure out if this is a class method is to check and see if
    the bound method im_self is a class, if so then we need to wrap the function
    object (im_func) with class method before setting it back on the class.

    '''
    if inspect.isclass(self._obj.im_self): # Figure out if this is a class method
      # Wrap it and set it back on the class
      setattr(self._instance, self._attr, classmethod(self._obj.im_func))
    else:
      setattr( self._instance, self._attr, self._obj )

class StubFunction(Stub):
  '''
  Stub a function.
  '''

  def __init__(self, obj, attr=None):
    '''
    Initialize with an object that is an unbound method
    '''
    super(StubFunction, self).__init__(obj, attr)
    if not self._attr:
      if getattr(obj, '__module__', None):
        self._instance = sys.modules[obj.__module__]
      elif getattr(obj, '__self__', None):
        self._instance = obj.__self__
      else:
        raise UnsupportedStub("Failed to find instance of %s"%(obj))

      if getattr(obj,'func_name', None):
        self._attr = obj.func_name
      elif getattr(obj,'__name__', None):
        self._attr = obj.__name__
      else:
        raise UnsupportedStub("Failed to find name of %s"%(obj))
    else:
      self._instance = self._obj
      self._obj = getattr(self._instance, self._attr)
    setattr( self._instance, self._attr, self )

  @property
  def name(self):
    return "%s.%s" % (self._instance.__name__, self._attr)

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

  @property
  def name(self):
    return "%s.%s" % (self._instance.__name__, self._attr)

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

  @property
  def name(self):
    return "%s.%s" % (self._instance.__class__.__name__, self._attr)

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

  @property
  def name(self):
    return "%s.%s" % (self._obj.__name__, self._attr)

  def teardown(self):
    '''
    Replace the original method.
    '''
    setattr( self._obj, self._attr, self._orig )

