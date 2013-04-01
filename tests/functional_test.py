# Simple functional tests

from chai import Chai
from chai.exception import UnexpectedCall

class FunctionalTest(Chai):

  def test_properties_using_attr_name_on_an_instance_only(self):
    class Foo(object):
      @property
      def prop(self): return 3
    
    foo = Foo()

    expect(foo, 'prop').returns('foo').times(1)
    assert_equals( 'foo', foo.prop )

    expect( stub(foo,'prop').setter ).args( 42 )
    foo.prop = 42
    expect( stub(foo,'prop').deleter )
    del foo.prop

    with assert_raises( UnexpectedCall ):
      foo.prop

  def test_properties_using_obj_ref_on_a_class_and_using_get_first(self):
    class Foo(object):
      @property
      def prop(self): return 3

    expect(Foo.prop).returns('foo').times(1)
    expect(Foo.prop.setter).args(42)
    expect(Foo.prop.deleter)

    assert_equals( 'foo', Foo().prop )
    Foo().prop = 42
    del Foo().prop
    assert_raises( UnexpectedCall, lambda: Foo().prop )

  def test_properties_using_obj_ref_on_a_class_and_using_set_first(self):
    class Foo(object):
      @property
      def prop(self): return 3

    expect(Foo.prop.setter).args(42)
    expect(Foo.prop).returns('foo')
    expect(Foo.prop.deleter)

    Foo().prop = 42
    assert_equals( 'foo', Foo().prop )
    del Foo().prop
