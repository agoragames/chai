# Simple functional tests

from chai import Chai

class FunctionalTest(Chai):

  def test_properties(self):
    class Foo(object):
      @property
      def prop(self): return 3
    
    foo = Foo()

    expect(foo, 'prop').returns('foo')
    self.assertEquals( 'foo', foo.prop )

    expect( stub(foo,'prop').setter ).args( 42 )
    foo.prop = 42
    expect( stub(foo,'prop').deleter )
    del foo.prop

