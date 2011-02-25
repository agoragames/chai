
import unittest
import types

from stub import *

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

  def test_stub_class_with_attr_name(self):
    class Foo(object):
      class Bar(object): pass

    res = stub(Foo, 'Bar')
    self.assertTrue( isinstance(res,StubClass) )
    # TODO: test that it caches once StubClass does stuff

  def test_stub_class_with_obj_ref(self):
    class Foo(object):
      class Bar(object): pass

    res = stub(Foo.Bar)
    self.assertTrue( isinstance(res,StubClass) )
    # TODO: test that it caches once StubClass does stuff

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
        super(StubIntercept,self).__call__(*args, **kwargs)

    orig = Foo.bar
    s = StubIntercept( Foo.bar )

    f1 = Foo()
    f1.bar()
    f2 = Foo()
    f2.bar()

    self.assertEquals( 2, s.calls )
