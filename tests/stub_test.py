
import unittest

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
