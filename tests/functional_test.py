# Simple functional tests
import sys
import unittest

from chai import Chai
from chai.exception import UnexpectedCall

try:
    IS_PYPY = sys.subversion[0]=='PyPy'
except AttributeError:
    IS_PYPY = False

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
    with assert_raises( UnexpectedCall ):
      Foo().prop

  @unittest.skipIf(IS_PYPY, "can't stub property setter in PyPy")
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

  def test_iterative_expectations(self):
    class Foo(object):
      def bar(self, x):
        return x
    f = Foo()

    assert_equals( 3, f.bar(3) )

    expect( f.bar )
    assert_equals( None, f.bar() )

    expect( f.bar ).returns( 4 )
    assert_equals( 4, f.bar() )
    assert_equals( 4, f.bar() )

    expect( f.bar ).returns( 5 ).times(1) 
    assert_equals( 5, f.bar() )
    with assert_raises( UnexpectedCall ):
      f.bar()

    expect( f.bar ).args( 6 ).returns( 7 )
    assert_equals( 7, f.bar(6) )

    expect( f.bar ).returns( 8 )
    expect( f.bar ).returns( 9 )
    assert_equals( 8, f.bar() )
    assert_equals( 9, f.bar() )
    assert_equals( 9, f.bar() )
