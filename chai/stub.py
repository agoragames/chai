'''
Copyright (c) 2011-2017, Agora Games, LLC All rights reserved.

https://github.com/agoragames/chai/blob/master/LICENSE.txt
'''
import inspect
import types
import sys
import gc

from .expectation import Expectation
from .spy import Spy
from .exception import *
from ._termcolor import colored

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
    Stub an attribute of an object. Will return an existing stub if
    there already is one.
    '''
    # Annoying circular reference requires importing here. Would like to see
    # this cleaned up. @AW
    from .mock import Mock

    # Check to see if this a property, this check is only for when dealing
    # with an instance. getattr will work for classes.
    is_property = False

    if not inspect.isclass(obj) and not inspect.ismodule(obj):
        # It's possible that the attribute is defined after initialization, and
        # so is not on the class itself.
        attr = getattr(obj.__class__, attr_name, None)
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

    # Sadly, builtin functions and methods have the same type, so we have to
    # use the same stub class even though it's a bit ugly
    if inspect.ismodule(obj) and isinstance(attr, (types.FunctionType,
                                            types.BuiltinFunctionType,
                                            types.BuiltinMethodType)):
        return StubFunction(obj, attr_name)

    # In python3 unbound methods are treated as functions with no reference
    # back to the parent class and no im_* fields. We can still make unbound
    # methods work by passing these through to the stub
    if inspect.isclass(obj) and isinstance(attr, types.FunctionType):
        return StubUnboundMethod(obj, attr_name)

    # I thought that types.UnboundMethodType differentiated these cases but
    # apparently not.
    if isinstance(attr, types.MethodType):
        # Handle differently if unbound because it's an implicit "any instance"
        if getattr(attr, 'im_self', None) is None:
            # Handle the python3 case and py2 filter
            if hasattr(attr, '__self__'):
                if attr.__self__ is not None:
                    return StubMethod(obj, attr_name)
            if sys.version_info.major == 2:
                return StubUnboundMethod(attr)
        else:
            return StubMethod(obj, attr_name)

    if isinstance(attr, (types.BuiltinFunctionType, types.BuiltinMethodType)):
        return StubFunction(obj, attr_name)

    # What an absurd type this is ....
    if type(attr).__name__ == 'method-wrapper':
        return StubMethodWrapper(attr)

    # This is also slot_descriptor
    if type(attr).__name__ == 'wrapper_descriptor':
        return StubWrapperDescriptor(obj, attr_name)

    raise UnsupportedStub(
        "can't stub %s(%s) of %s", attr_name, type(attr), obj)


def _stub_obj(obj):
    '''
    Stub an object directly.
    '''
    # Annoying circular reference requires importing here. Would like to see
    # this cleaned up. @AW
    from .mock import Mock

    # Return an existing stub
    if isinstance(obj, Stub):
        return obj

    # If a Mock object, stub its __call__
    if isinstance(obj, Mock):
        return stub(obj.__call__)

    # If passed-in a type, assume that we're going to stub out the creation.
    # See StubNew for the awesome sauce.
    # if isinstance(obj, types.TypeType):
    if hasattr(types, 'TypeType') and isinstance(obj, types.TypeType):
        return StubNew(obj)
    elif hasattr(__builtins__, 'type') and \
            isinstance(obj, __builtins__.type):
        return StubNew(obj)
    elif inspect.isclass(obj):
        return StubNew(obj)

    # I thought that types.UnboundMethodType differentiated these cases but
    # apparently not.
    if isinstance(obj, types.MethodType):
        # Handle differently if unbound because it's an implicit "any instance"
        if getattr(obj, 'im_self', None) is None:
            # Handle the python3 case and py2 filter
            if hasattr(obj, '__self__'):
                if obj.__self__ is not None:
                    return StubMethod(obj)
            if sys.version_info.major == 2:
                return StubUnboundMethod(obj)
        else:
            return StubMethod(obj)

    # These aren't in the types library
    if type(obj).__name__ == 'method-wrapper':
        return StubMethodWrapper(obj)

    if type(obj).__name__ == 'wrapper_descriptor':
        raise UnsupportedStub(
            "must call stub(obj,'%s') for slot wrapper on %s",
            obj.__name__, obj.__objclass__.__name__)

    # (Mostly) Lastly, look for properties.
    # First look for the situation where there's a reference back to the
    # property.
    prop = obj
    if isinstance(getattr(obj, '__self__', None), property):
        obj = prop.__self__

    # Once we've found a property, we have to figure out how to reference
    # back to the owning class. This is a giant pain and we have to use gc
    # to find out where it comes from. This code is dense but resolves to
    # something like this:
    # >>> gc.get_referrers( foo.x )
    # [{'__dict__': <attribute '__dict__' of 'foo' objects>,
    #   'x': <property object at 0x7f68c99a16d8>,
    #   '__module__': '__main__',
    #   '__weakref__': <attribute '__weakref__' of 'foo' objects>,
    #   '__doc__': None}]
    if isinstance(obj, property):
        klass, attr = None, None
        for ref in gc.get_referrers(obj):
            if klass and attr:
                break
            if isinstance(ref, dict) and ref.get('prop', None) is obj:
                klass = getattr(
                    ref.get('__dict__', None), '__objclass__', None)
                for name, val in getattr(klass, '__dict__', {}).items():
                    if val is obj:
                        attr = name
                        break
            # In the case of PyPy, we have to check all types that refer to
            # the property, and see if any of their attrs are the property
            elif isinstance(ref, type):
                # Use dir as a means to quickly walk through the class tree
                for name in dir(ref):
                    if getattr(ref, name) == obj:
                        klass = ref
                        attr = name
                        break

        if klass and attr:
            rval = stub(klass, attr)
            if prop != obj:
                return stub(rval, prop.__name__)
            return rval

    # If a function and it has an associated module, we can mock directly.
    # Note that this *must* be after properties, otherwise it conflicts with
    # stubbing out the deleter methods and such
    # Sadly, builtin functions and methods have the same type, so we have to
    # use the same stub class even though it's a bit ugly
    if isinstance(obj, (types.FunctionType, types.BuiltinFunctionType,
                  types.BuiltinMethodType)) and hasattr(obj, '__module__'):
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
        self._torn = False

    @property
    def name(self):
        return None  # The base class implement this.

    @property
    def expectations(self):
        return self._expectations

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
        Clean up all expectations and restore the original attribute of the
        mocked object.
        '''
        if not self._torn:
            self._expectations = []
            self._torn = True
            self._teardown()

    def _teardown(self):
        '''
        Hook for subclasses to teardown their stubs. Called only once.
        '''

    def expect(self):
        '''
        Add an expectation to this stub. Return the expectation.
        '''
        exp = Expectation(self)
        self._expectations.append(exp)
        return exp

    def spy(self):
        '''
        Add a spy to this stub. Return the spy.
        '''
        spy = Spy(self)
        self._expectations.append(spy)
        return spy

    def call_orig(self, *args, **kwargs):
        '''
        Calls the original function.
        '''
        raise NotImplementedError("Must be implemented by subclasses")

    def __call__(self, *args, **kwargs):
        for exp in self._expectations:
            # If expectation closed skip
            if exp.closed():
                continue

            # If args don't match the expectation but its minimum counts have
            # been met, close it and move on, else it's an unexpected call.
            # Have to check counts here now due to the looser definitions of
            # expectations in 0.3.x If we dont match, the counts aren't met
            # and we're not allowing out-of-order, then break out and raise
            # an exception.
            if not exp.match(*args, **kwargs):
                if exp.counts_met():
                    exp.close(*args, **kwargs)
                elif not exp.is_any_order():
                    break
            else:
                return exp.test(*args, **kwargs)

        raise UnexpectedCall(
            call=self.name, suffix=self._format_exception(),
            args=args, kwargs=kwargs)

    def _format_exception(self):
        result = [
            colored("All expectations", 'white', attrs=['bold'])
        ]
        for e in self._expectations:
            result.append(str(e))
        return "\n".join(result)


class StubProperty(Stub, property):

    '''
    Property stubbing.
    '''

    def __init__(self, obj, attr):
        super(StubProperty, self).__init__(obj, attr)
        property.__init__(self, lambda x: self(),
                          lambda x, val: self.setter(val),
                          lambda x: self.deleter())
        # In order to stub out a property we have ask the class for the
        # propery object that was created we python execute class code.
        if inspect.isclass(obj):
            self._instance = obj
        else:
            self._instance = obj.__class__

        # Use a simple Mock object for the deleter and setter. Use same
        # namespace as property type so that it simply works.
        # Annoying circular reference requires importing here. Would like to
        # see this cleaned up. @AW
        from .mock import Mock
        self._obj = getattr(self._instance, attr)
        self.setter = Mock()
        self.deleter = Mock()

        setattr(self._instance, self._attr, self)

    def call_orig(self, *args, **kwargs):
        '''
        Calls the original function.
        '''
        # TODO: this is probably the most complicated one to implement. Will
        # figure it out eventually.
        raise NotImplementedError("property spies are not supported")

    @property
    def name(self):
        return "%s.%s" % (self._instance.__name__, self._attr)

    def _teardown(self):
        '''
        Replace the original method.
        '''
        setattr(self._instance, self._attr, self._obj)


class StubMethod(Stub):

    '''
    Stub a method.
    '''

    def __init__(self, obj, attr=None):
        '''
        Initialize with an object of type MethodType
        '''
        super(StubMethod, self).__init__(obj, attr)
        if not self._attr:
            # python3
            if sys.version_info.major == 3:  # hasattr(obj,'__func__'):
                self._attr = obj.__func__.__name__
            else:
                self._attr = obj.im_func.func_name

            if sys.version_info.major == 3:  # hasattr(obj, '__self__'):
                self._instance = obj.__self__
            else:
                self._instance = obj.im_self
        else:
            self._instance = self._obj
            self._obj = getattr(self._instance, self._attr)
        setattr(self._instance, self._attr, self)

    @property
    def name(self):
        from .mock import Mock  # Import here for the same reason as above.
        if hasattr(self._obj, 'im_class'):
            if issubclass(self._obj.im_class, Mock):
                return self._obj.im_self._name

        # Always use the class to get the name
        klass = self._instance
        if not inspect.isclass(self._instance):
            klass = self._instance.__class__

        return "%s.%s" % (klass.__name__, self._attr)

    def call_orig(self, *args, **kwargs):
        '''
        Calls the original function.
        '''
        if hasattr(self._obj, '__self__') and \
                inspect.isclass(self._obj.__self__) and \
                self._obj.__self__ is self._instance:
            return self._obj.__func__(self._instance, *args, **kwargs)
        elif hasattr(self._obj, 'im_self') and \
                inspect.isclass(self._obj.im_self) and \
                self._obj.im_self is self._instance:
            return self._obj.im_func(self._instance, *args, **kwargs)
        else:
            return self._obj(*args, **kwargs)

    def _teardown(self):
        '''
        Put the original method back in place. This will also handle the
        special case when it putting back a class method.

        The following code snippet best describe why it fails using settar,
        the class method would be replaced with a bound method not a class
        method.

        >>> class Example(object):
        ...     @classmethod
        ...     def a_classmethod(self):
        ...         pass
        ...
        >>> Example.__dict__['a_classmethod']
        <classmethod object at 0x7f5e6c298be8>
        >>> orig = getattr(Example, 'a_classmethod')
        >>> orig
        <bound method type.a_classmethod of <class '__main__.Example'>>
        >>> setattr(Example, 'a_classmethod', orig)
        >>> Example.__dict__['a_classmethod']
        <bound method type.a_classmethod of <class '__main__.Example'>>

        The only way to figure out if this is a class method is to check and
        see if the bound method im_self is a class, if so then we need to wrap
        the function object (im_func) with class method before setting it back
        on the class.
        '''
        # Figure out if this is a class method and we're unstubbing it on the
        # class to which it belongs. This addresses an edge case where a
        # module can expose a method of an instance. e.g gevent.
        if hasattr(self._obj, '__self__') and \
                inspect.isclass(self._obj.__self__) and \
                self._obj.__self__ is self._instance:
            setattr(
                self._instance, self._attr, classmethod(self._obj.__func__))
        elif hasattr(self._obj, 'im_self') and \
                inspect.isclass(self._obj.im_self) and \
                self._obj.im_self is self._instance:
            # Wrap it and set it back on the class
            setattr(self._instance, self._attr, classmethod(self._obj.im_func))
        else:
            setattr(self._instance, self._attr, self._obj)


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
                raise UnsupportedStub("Failed to find instance of %s" % (obj))

            if getattr(obj, 'func_name', None):
                self._attr = obj.func_name
            elif getattr(obj, '__name__', None):
                self._attr = obj.__name__
            else:
                raise UnsupportedStub("Failed to find name of %s" % (obj))
        else:
            self._instance = self._obj
            self._obj = getattr(self._instance, self._attr)

        # This handles the case where we're stubbing a special method that's
        # inherited from object, and so instead of calling setattr on teardown,
        # we want to call delattr. This is particularly important for not
        # seeing those stupid DeprecationWarnings after StubNew
        self._was_object_method = False
        if hasattr(self._instance, '__dict__'):
            self._was_object_method = \
                self._attr not in self._instance.__dict__.keys() and\
                self._attr in object.__dict__.keys()
        setattr(self._instance, self._attr, self)

    @property
    def name(self):
        return "%s.%s" % (self._instance.__name__, self._attr)

    def call_orig(self, *args, **kwargs):
        '''
        Calls the original function.
        '''
        # TODO: Does this change if was_object_method?
        return self._obj(*args, **kwargs)

    def _teardown(self):
        '''
        Replace the original method.
        '''
        if not self._was_object_method:
            setattr(self._instance, self._attr, self._obj)
        else:
            delattr(self._instance, self._attr)


class StubNew(StubFunction):

    '''
    Stub out the constructor, but hide the fact that we're stubbing "__new__"
    and act more like we're stubbing "__init__". Needs to use the logic in
    the StubFunction ctor.
    '''
    _cache = {}

    def __new__(self, klass, *args):
        '''
        Because we're not saving the stub into any attribute, then we have
        to do some faking here to return the same handle.
        '''
        rval = self._cache.get(klass)
        if not rval:
            rval = self._cache[klass] = super(
                StubNew, self).__new__(self, *args)
            rval._allow_init = True
        else:
            rval._allow_init = False
        return rval

    def __init__(self, obj):
        '''
        Overload the initialization so that we can hack access to __new__.
        '''
        if self._allow_init:
            self._new = obj.__new__
            super(StubNew, self).__init__(obj, '__new__')
            self._type = obj

    def __call__(self, *args, **kwargs):
        '''
        When calling the new function, strip out the first arg which is
        the type. In this way, the mocker writes their expectation as if it
        was an __init__.
        '''
        return super(StubNew, self).__call__(*(args[1:]), **kwargs)

    def call_orig(self, *args, **kwargs):
        '''
        Calls the original function. Simulates __new__ and __init__ together.
        '''
        rval = super(StubNew, self).call_orig(self._type)
        rval.__init__(*args, **kwargs)
        return rval

    def _teardown(self):
        '''
        Overload so that we can clear out the cache after a test run.
        '''
        # __new__ is a super-special case in that even when stubbing a class
        # which implements its own __new__ and subclasses object, the
        # "Class.__new__" reference is a staticmethod and not a method (or
        # function). That confuses the "was_object_method" logic in
        # StubFunction which then fails to delattr and from then on the class
        # is corrupted. So skip that teardown and use a __new__-specific case.
        setattr(self._instance, self._attr, staticmethod(self._new))
        StubNew._cache.pop(self._type)


class StubUnboundMethod(Stub):

    '''
    Stub an unbound method.
    '''

    def __init__(self, obj, attr=None):
        '''
        Initialize with an object that is an unbound method
        '''
        # Note: It doesn't appear that there's any way to support stubbing
        # by method in python3 because an unbound method has no reference
        # to its parent class, it just looks like a regular function
        super(StubUnboundMethod, self).__init__(obj, attr)
        if self._attr is None:
            self._instance = obj.im_class
            self._attr = obj.im_func.func_name
        else:
            self._obj = getattr(obj, attr)
            self._instance = obj
        setattr(self._instance, self._attr, self)

    @property
    def name(self):
        return "%s.%s" % (self._instance.__name__, self._attr)

    def call_orig(self, *args, **kwargs):
        '''
        Calls the original function.
        '''
        # TODO: Figure out if this can be implemented. The challenge is that
        # the context of "self" has to be passed in as an argument, but there's
        # not necessarily a generic way of doing that. It may fall out as a
        # side-effect of the actual implementation of spies.
        raise NotImplementedError("unbound method spies are not supported")

    def _teardown(self):
        '''
        Replace the original method.
        '''
        setattr(self._instance, self._attr, self._obj)


class StubMethodWrapper(Stub):

    '''
    Stub a method-wrapper.
    '''

    def __init__(self, obj):
        '''
        Initialize with an object that is a method wrapper.
        '''
        super(StubMethodWrapper, self).__init__(obj)
        self._instance = obj.__self__
        self._attr = obj.__name__
        setattr(self._instance, self._attr, self)

    @property
    def name(self):
        return "%s.%s" % (self._instance.__class__.__name__, self._attr)

    def call_orig(self, *args, **kwargs):
        '''
        Calls the original function.
        '''
        return self._obj(*args, **kwargs)

    def _teardown(self):
        '''
        Replace the original method.
        '''
        setattr(self._instance, self._attr, self._obj)


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
        super(StubWrapperDescriptor, self).__init__(obj, attr_name)
        self._orig = getattr(self._obj, self._attr)
        setattr(self._obj, self._attr, self)

    @property
    def name(self):
        return "%s.%s" % (self._obj.__name__, self._attr)

    def call_orig(self, *args, **kwargs):
        '''
        Calls the original function.
        '''
        return self._orig(self._obj, *args, **kwargs)

    def _teardown(self):
        '''
        Replace the original method.
        '''
        setattr(self._obj, self._attr, self._orig)
