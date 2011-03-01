
import unittest
import types

from chai.stub import *
import samples

class StubTest(unittest.TestCase):
  ###
  ### Test the public stub() method
  ###
  def test_stub_property_with_attr_name(self):
    class Foo(object):
      @property
      def prop(self): return 3

    res = stub(Foo, 'prop')
    self.assertTrue( isinstance(res,StubProperty) )
    self.assertEquals( res, stub(Foo,'prop') )
    self.assertEquals( res, getattr(Foo,'prop') )

  def test_stub_property_raises_unsupported_with_obj_ref(self):
    class Foo(object):
      @property
      def prop(self): return 3

    self.assertRaises( UnsupportedStub, stub, Foo.prop)

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
    res = stub(foo, 'bar')
    self.assertTrue( isinstance(res,StubMethod) )
    self.assertEquals( res, stub(foo,'bar') )
    self.assertEquals( res, getattr(foo,'bar') )

  def test_stub_bound_method_for_instance_with_obj_ref(self):
    class Foo(object):
      def bar(self): pass

    foo = Foo()
    res = stub(foo.bar)
    self.assertTrue( isinstance(res,StubMethod) )
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
  
  ###
  ### Test Stub class (if only I could mock my mocking mocks)
  ###
  def test_init(self):
    s = Stub('obj','attr')
    self.assertEquals( 'obj', s._obj )
    self.assertEquals( 'attr', s._attr )
    self.assertEquals( [], s._expectations )

  def test_assert_expectations(self):
    s = Stub('obj', 'attr')
    s.expect().args(123).returns(1)
    
    self.assertRaises(ExpectationNotSatisfied, s.assert_expectations)
  
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
    

class StubMethodTest(unittest.TestCase):
  
  def test_init(self):
    class Foo(object):
      def bar(self): pass

    f = Foo()
    s = StubMethod( f.bar )
    self.assertEquals( s._instance, f )
    self.assertEquals( s._attr, 'bar' )
    self.assertEquals( s, getattr(f,'bar') )

  def test_teardown(self):
    class Foo(object):
      def bar(self): pass

    f = Foo()
    orig = f.bar
    s = StubMethod( f.bar )
    s.teardown()
    self.assertEquals( orig, f.bar )

class StubUnboundMethodTest(unittest.TestCase):
  
  def test_init(self):
    class Foo(object):
      def bar(self): pass

    s = StubUnboundMethod( Foo.bar )
    self.assertEquals( s._instance, Foo )
    self.assertEquals( s._attr, 'bar' )
    self.assertEquals( s, getattr(Foo,'bar') )

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
