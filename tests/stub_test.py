import re
import unittest
import types

from chai.stub import *
from chai.mock import Mock
import samples

class StubTest(unittest.TestCase):
  ###
  ### Test the public stub() method
  ###
  def test_stub_property_on_class_with_attr_name(self):
    class Foo(object):
      @property
      def prop(self): return 3
    
    res = stub(Foo, 'prop')
    self.assertTrue( isinstance(res,StubProperty) )
    self.assertTrue( stub(Foo,'prop') is res )

  def test_stub_property_on_instance_with_attr_name(self):
    class Foo(object):
      @property
      def prop(self): return 3
    foo = Foo()
    
    res = stub(foo, 'prop')
    self.assertTrue( isinstance(res,StubProperty) )
    self.assertTrue( stub(foo,'prop') is res )

  def test_stub_property_on_class_with_attr_name_applies_to_instance(self):
    class Foo(object):
      @property
      def prop(self): return 3
    
    foo = Foo()
    res = stub(Foo, 'prop')
    self.assertTrue( stub(foo,'prop') is res )

  def test_stub_property_with_obj_ref_for_the_reader(self):
    class Foo(object):
      @property
      def prop(self): return 3

    res = stub(Foo.prop)
    self.assertTrue( isinstance(res, StubProperty) )
    self.assertTrue( stub(Foo.prop) is res )

  def test_stub_property_with_obj_ref_for_the_setter(self):
    class Foo(object):
      @property
      def prop(self): return 3

    res = stub(Foo.prop.setter)
    self.assertTrue( isinstance(res, StubMethod) )
    self.assertTrue( isinstance(Foo.prop, StubProperty) )

  def test_stub_property_with_obj_ref_for_the_deleter(self):
    class Foo(object):
      @property
      def prop(self): return 3

    res = stub(Foo.prop.deleter)
    self.assertTrue( isinstance(res, StubMethod) )
    self.assertTrue( isinstance(Foo.prop, StubProperty) )

  def test_stub_mock_with_attr_name(self):
    class Foo(object):
      def bar(self): pass

    f = Foo()
    f.bar = Mock()
    res = stub(f, 'bar')
    self.assertTrue( isinstance(res, StubMethod) )
    self.assertEquals( res, f.bar.__call__ )
    self.assertEquals( res, stub(f, 'bar') )

  def test_stub_mock_with_obj_ref(self):
    class Foo(object):
      def bar(self): pass

    f = Foo()
    f.bar = Mock()
    res = stub(f.bar)
    self.assertTrue( isinstance(res, StubMethod) )
    self.assertEquals( res, f.bar.__call__ )
    self.assertEquals( res, stub(f.bar) )

  def test_stub_type_with_obj_ref(self):
    class Foo(object):
      def bar(self): pass

    res = stub( Foo )
    self.assertTrue( isinstance(res, StubNew) )
    self.assertEquals( res, Foo.__new__ )
    self.assertEquals( res, stub(Foo) )

  def test_stub_unbound_method_with_attr_name(self):
    class Foo(object):
      def bar(self): pass

    res = stub(Foo, 'bar')
    self.assertTrue( isinstance(res,StubUnboundMethod) )
    self.assertEquals( res, stub(Foo,'bar') )
    self.assertEquals( res, getattr(Foo,'bar') )

  def test_stub_unbound_method_with_obj_ref(self):
    class Foo(object):
      def bar(self): pass

    res = stub(Foo.bar)
    self.assertTrue( isinstance(res,StubUnboundMethod) )
    self.assertEquals( res, stub(Foo.bar) )
    self.assertEquals( res, getattr(Foo,'bar') )

  def test_stub_bound_method_for_instance_with_attr_name(self):
    class Foo(object):
      def bar(self): pass

    foo = Foo()
    orig = foo.bar
    res = stub(foo, 'bar')
    self.assertTrue( isinstance(res,StubMethod) )
    self.assertEquals( res._instance, foo )
    self.assertEquals( res._obj, orig )
    self.assertEquals( res._attr, 'bar' )
    self.assertEquals( res, stub(foo,'bar') )
    self.assertEquals( res, getattr(foo,'bar') )

  def test_stub_bound_method_for_instance_with_obj_ref(self):
    class Foo(object):
      def bar(self): pass

    foo = Foo()
    orig = foo.bar
    res = stub(foo.bar)
    self.assertTrue( isinstance(res,StubMethod) )
    self.assertEquals( res._instance, foo )
    self.assertEquals( res._obj, orig )
    self.assertEquals( res._attr, 'bar' )
    self.assertEquals( res, stub(foo.bar) )
    self.assertEquals( res, getattr(foo,'bar') )

  def test_stub_bound_method_for_classmethod_with_attr_name(self):
    class Foo(object):
      @classmethod
      def bar(self): pass

    res = stub(Foo, 'bar')
    self.assertTrue( isinstance(res,StubMethod) )
    self.assertEquals( res, stub(Foo,'bar') )
    self.assertEquals( res, getattr(Foo,'bar') )

  def test_stub_bound_method_for_classmethod_with_obj_ref(self):
    class Foo(object):
      @classmethod
      def bar(self): pass

    res = stub(Foo.bar)
    self.assertTrue( isinstance(res,StubMethod) )
    self.assertEquals( res, stub(Foo.bar) )
    self.assertEquals( res, getattr(Foo,'bar') )

  def test_stub_method_wrapper_with_attr_name(self):
    class Foo(object): pass

    foo = Foo()
    res = stub(foo, '__hash__')
    self.assertTrue( isinstance(res,StubMethodWrapper) )
    self.assertEquals( res, stub(foo, '__hash__') )
    self.assertEquals( res, getattr(foo, '__hash__') )

  def test_stub_method_wrapper_with_obj_ref(self):
    class Foo(object): pass

    foo = Foo()
    res = stub(foo.__hash__)
    self.assertTrue( isinstance(res,StubMethodWrapper) )
    self.assertEquals( res, stub(foo.__hash__) )
    self.assertEquals( res, getattr(foo, '__hash__') )

  def test_stub_module_function_with_attr_name(self):
    res = stub(samples, 'mod_func_1')
    self.assertTrue( isinstance(res,StubFunction) )
    self.assertEquals( res, getattr(samples,'mod_func_1') )
    self.assertEquals( res, stub(samples,'mod_func_1') )

  def test_stub_module_function_with_obj_ref(self):
    res = stub(samples.mod_func_1) 
    self.assertTrue( isinstance(res,StubFunction) )
    self.assertEquals( res, getattr(samples,'mod_func_1') )
    self.assertEquals( res, samples.mod_func_1 )
    self.assertEquals( res, stub(samples.mod_func_1) )
  
class StubClassTest(unittest.TestCase):
  ###
  ### Test Stub class (if only I could mock my mocking mocks)
  ###
  def test_init(self):
    s = Stub('obj','attr')
    self.assertEquals( 'obj', s._obj )
    self.assertEquals( 'attr', s._attr )
    self.assertEquals( [], s._expectations )

  def test_unment_expectations(self):
    s = Stub('obj', 'attr')
    s.expect().args(123).returns(1)
    
    self.assertTrue(all([isinstance(e, ExpectationNotSatisfied) for e in s.unmet_expectations()]))
  
  def test_teardown(self):
    s = Stub('obj')
    s._expections = ['1','2']
    s.teardown()
    self.assertEquals( [], s._expectations )

  def test_expect(self):
    s = Stub('obj')

    self.assertEquals( [], s._expectations )
    e = s.expect()
    self.assertEquals( [e], s._expectations )
    self.assertEquals( s, e._stub )

  def test_call_raises_unexpected_call_when_no_expectations(self):
    s = Stub('obj')
    self.assertRaises( UnexpectedCall, s, 'foo' )

  def test_call_when_args_match(self):
    class Expect(object):
      def closed(self): return False
      def match(self, *args, **kwargs): return True
      def test(self, *args, **kwargs): return 'success'
    
    s = Stub('obj')
    s._expectations = [ Expect() ]
    self.assertEquals( 'success', s('foo') )
  
  def test_call_raises_unexpected_call_when_all_expectations_closed(self):
    class Expect(object):
      def closed(self): return True
    
    s = Stub('obj')
    s._expectations = [ Expect(), Expect() ]
    self.assertRaises( UnexpectedCall, s, 'foo' )

  def test_call_raises_unexpected_call_when_closed_and_no_matching(self):
    class Expect(object):
      def __init__(self, closed): 
        self._closed=closed
        self._match_count = 0
        self._close_count=0
      def closed(self):
        return self._closed
      def match(self, *args, **kwargs):
        self._match_count +=1
        return False
      def close(self, *args, **kwargs):
        self._close_count += 1
        self._close_args = (args,kwargs)
    
    s = Stub('obj')
    s._expectations = [ Expect(True), Expect(False) ]
    self.assertRaises( UnexpectedCall, s, 'foo' )
    self.assertEquals( 0, s._expectations[0]._match_count )
    self.assertEquals( 1, s._expectations[1]._match_count )
    self.assertEquals( 0, s._expectations[0]._close_count )
    self.assertEquals( 1, s._expectations[1]._close_count )
    self.assertEquals( (('foo',),{}), s._expectations[1]._close_args )
    

class StubPropertyTest(unittest.TestCase):
  # FIXME: Need to test teardown and init, these test might be in the base stub tests.
  
  def test_name(self):
    class Foo(object):
      @property
      def prop(self): return 3
    
    s = StubProperty(Foo, 'prop')
    self.assertEquals(s.name, 'Foo.prop')

class StubMethodTest(unittest.TestCase):
  
  def test_init(self):
    class Foo(object):
      def bar(self): pass

    f = Foo()
    orig = f.bar
    s = StubMethod( f.bar )
    self.assertEquals( s._obj, orig )
    self.assertEquals( s._instance, f )
    self.assertEquals( s._attr, 'bar' )
    self.assertEquals( s, getattr(f,'bar') )
    
    f = Foo()
    orig = f.bar
    s = StubMethod( f, 'bar' )
    self.assertEquals( s._obj, orig )
    self.assertEquals( s._instance, f )
    self.assertEquals( s._attr, 'bar' )
    self.assertEquals( s, getattr(f,'bar') )

  def test_name(self):
    class Expect(object):
      def closed(self): return False
    obj = Expect()
    s = StubMethod(obj.closed)
    self.assertEquals("Expect.closed", s.name)
    s.teardown()

    s = StubMethod(obj, 'closed')
    self.assertEquals("Expect.closed", s.name)
    s.teardown()

  def test_teardown(self):
    class Foo(object):
      def bar(self): pass

    f = Foo()
    orig = f.bar
    s = StubMethod( f.bar )
    s.teardown()
    self.assertEquals( orig, f.bar )

  def test_teardown_of_classmethods(self):
    class Foo(object):
      @classmethod
      def bar(self): pass
    
    self.assertTrue(isinstance(Foo.__dict__['bar'], classmethod))
    s = StubMethod( Foo.bar )
    s.teardown()
    self.assertTrue(isinstance(Foo.__dict__['bar'], classmethod), "Is not a classmethod")

  def test_teardown_of_bound_instance_methods_exported_in_module(self):
    orig = samples.mod_instance_foo
    s = StubMethod( samples, 'mod_instance_foo' )
    s.teardown()
    self.assertEquals( orig, samples.mod_instance_foo )

class StubFunctionTest(unittest.TestCase):

  def test_init(self):
    s = StubFunction( samples.mod_func_1 )
    self.assertEquals( s._instance, samples )
    self.assertEquals( s._attr, 'mod_func_1' )
    self.assertEquals( s, samples.mod_func_1 )
    self.assertEquals( False, s._was_object_method )
    s.teardown()

  def test_init_with_object_method(self):
    x = samples.SampleBase()
    s = StubFunction( x, '__new__' )
    self.assertEquals( True, s._was_object_method )

  def test_name(self):
    s = StubFunction( samples.mod_func_1 )
    self.assertEquals( 'tests.samples.mod_func_1', s.name )
    s.teardown()

  def test_teardown(self):
    orig = samples.mod_func_1
    s = StubFunction( samples.mod_func_1 )
    s.teardown()
    self.assertEquals( orig, samples.mod_func_1 )

  def test_teardown_on_object_method(self):
    x = samples.SampleBase()
    self.assertEquals( object.__new__, getattr(x, '__new__') )
    s = StubFunction( x, '__new__' )
    self.assertNotEquals( object.__new__, getattr(x, '__new__') )
    s.teardown()
    self.assertEquals( object.__new__, getattr(x, '__new__') )

class StubNewTest(unittest.TestCase):

  def test_new(self):
    class Foo(object): pass

    self.assertEquals( 0, len(StubNew._cache) )
    x = StubNew(Foo)
    self.assertTrue( x is StubNew(Foo) )
    self.assertEquals( 1, len(StubNew._cache) )
    StubNew._cache.clear()

  def test_init(self):
    class Foo(object): pass
    
    s = StubNew( Foo )
    self.assertEquals( s._instance, Foo )
    self.assertEquals( s._attr, '__new__' )
    self.assertEquals( s, Foo.__new__ )
    s.teardown()

  def test_call(self):
    class Foo(object): pass
    class Expect(object):
      def closed(self): return False
      def match(self, *args, **kwargs): return args==('state',) and kwargs=={'a':'b'}
      def test(self, *args, **kwargs): return 'success'
    
    s = StubNew( Foo )
    s._expectations = [ Expect() ]
    self.assertEquals( 'success', Foo('state', a='b') )
    s.teardown()

  def test_teardown(self):
    class Foo(object): pass

    orig = Foo.__new__
    self.assertEquals( 0, len(StubNew._cache) )
    x = StubNew(Foo)
    self.assertEquals( 1, len(StubNew._cache) )
    x.teardown()
    self.assertEquals( 0, len(StubNew._cache) )
    self.assertEquals( orig, Foo.__new__ )

class StubUnboundMethodTest(unittest.TestCase):
  
  def test_init(self):
    class Foo(object):
      def bar(self): pass

    s = StubUnboundMethod( Foo.bar )
    self.assertEquals( s._instance, Foo )
    self.assertEquals( s._attr, 'bar' )
    self.assertEquals( s, getattr(Foo,'bar') )

  def test_name(self):
    class Expect(object):
      def closed(self): return False

    s = StubUnboundMethod(Expect.closed)
    self.assertEquals("Expect.closed", s.name)
    s.teardown()

  def test_teardown(self):
    class Foo(object):
      def bar(self): pass

    orig = Foo.bar
    s = StubUnboundMethod( Foo.bar )
    s.teardown()
    self.assertEquals( orig, Foo.bar )

  def test_call_acts_as_any_instance(self):
    class Foo(object):
      def bar(self): pass

    class StubIntercept(StubUnboundMethod):
      calls = 0
      def __call__(self, *args, **kwargs):
        self.calls += 1

    orig = Foo.bar
    s = StubIntercept( Foo.bar )

    f1 = Foo()
    f1.bar()
    f2 = Foo()
    f2.bar()

    self.assertEquals( 2, s.calls )

class StubMethodWrapperTest(unittest.TestCase):
  
  def test_init(self):
    class Foo(object):pass
    foo = Foo()

    s = StubMethodWrapper( foo.__hash__ )
    self.assertEquals( s._instance, foo )
    self.assertEquals( s._attr, '__hash__' )
    self.assertEquals( s, getattr(foo,'__hash__') )

  def test_name(self):
    class Foo(object):pass
    foo = Foo()

    s = StubMethodWrapper(foo.__hash__)
    self.assertEquals("Foo.__hash__", s.name)
    s.teardown()

  def test_teardown(self):
    class Foo(object):pass
    obj = Foo()
    orig = obj.__hash__
    s = StubMethodWrapper( obj.__hash__ )
    s.teardown()
    self.assertEquals( orig, obj.__hash__)

class StubMethodWrapperDescriptionTest(unittest.TestCase):
  
  def test_init(self):
    class Foo(object):pass
    s = StubWrapperDescriptor( Foo, '__hash__' )
    self.assertEquals( s._obj, Foo )
    self.assertEquals( s._attr, '__hash__' )
    self.assertEquals( s, getattr(Foo,'__hash__') )

  def test_name(self):
    class Foo(object):pass

    s = StubWrapperDescriptor(Foo, '__hash__')
    self.assertEquals("Foo.__hash__", s.name)
    s.teardown()

  def test_teardown(self):
    class Foo(object):pass
    orig = Foo.__hash__
    s = StubWrapperDescriptor( Foo, '__hash__' )
    s.teardown()
    self.assertEquals( orig, Foo.__hash__)
