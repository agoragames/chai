
import unittest

from chai.comparators import *

class ComparatorsTest(unittest.TestCase):
  
  def test_build_comparators_builds_equals(self):
    comp = build_comparators("str")[0]
    self.assertTrue(isinstance(comp, Equals))
    comp = build_comparators(12)[0]
    self.assertTrue(isinstance(comp, Equals))
    comp = build_comparators(12.1)[0]
    self.assertTrue(isinstance(comp, Equals))
    comp = build_comparators([])[0]
    self.assertTrue(isinstance(comp, Equals))
    comp = build_comparators({})[0]
    self.assertTrue(isinstance(comp, Equals))
    comp = build_comparators(tuple())[0]
    self.assertTrue(isinstance(comp, Equals))
  
  def test_build_comparators_is_a(self):
    class CustomObject(object): pass
    comp = build_comparators(CustomObject)[0]
    self.assertTrue(isinstance(comp, IsA))
    
  def test_build_comparators_passes_comparators(self):
    any_comp = Any()
    comp = build_comparators(any_comp)[0]
    self.assertTrue(comp is any_comp)

  def test_equals(self):
    comp = Equals(3)
    self.assertTrue( comp.test(3) )
    self.assertTrue( comp.test(3.0) )
    self.assertFalse( comp.test('3') )
  
  def test_equals_repr(self):
      comp = Equals(3)
      self.assertEquals(str(comp), "3")

  def test_eq(self):
    comp = Equals(3)
    self.assertEquals( comp, 3 )

  def test_is_a(self):
    comp = IsA(str)
    self.assertTrue( comp.test('foo') )
    self.assertFalse( comp.test(u'foo') )
    self.assertFalse( comp.test(bytearray('foo')) )
    
    comp = IsA((str,int))
    self.assertTrue( comp.test('') )
    self.assertTrue( comp.test(42) )
    self.assertFalse( comp.test(3.14) )

  def test_is_a_repr(self):
    comp = IsA(str)
    self.assertEquals(repr(comp), "IsA(str)")
    
  def test_is_a_format_name(self):
    comp = IsA(str)
    self.assertEquals(comp._format_name(), "str")
    comp = IsA((str, list))
    self.assertEquals(comp._format_name(), "['str', 'list']")

  def test_is(self):
    class Test(object):
      def __eq__(self, other): return True

    obj1 = Test()
    obj2 = Test()
    comp = Is(obj1)
    self.assertEquals( obj1, obj2 )
    self.assertTrue( comp.test(obj1) )
    self.assertFalse( comp.test(obj2) )
  
  def test_is_repr(self):
    class TestObj(object):
      
      def __str__(self):
        return "An Object"
    
    obj = TestObj()
    self.assertEquals(repr(Is(obj)), "Is(An Object)" )

  def test_almost_equal(self):
    comp = AlmostEqual(3.14159265, 3)
    self.assertTrue( comp.test(3.1416) )
    self.assertFalse( comp.test(3.14) )
  
  def test_almost_equal_repr(self):
    comp = AlmostEqual(3.14159265, 3)
    self.assertEquals(repr(comp), "AlmostEqual(value: 3.14159265, places: 3)")
  
  def test_regex(self):
    comp = Regex('[wf][io]{2}')
    self.assertTrue( comp.test('fii') )
    self.assertTrue( comp.test('woo') )
    self.assertFalse( comp.test('fuu') )

  def test_regex_repr(self):
    comp = Regex('[wf][io]{2}')
    self.assertEquals(repr(comp), "Regex(pattern: [wf][io]{2}, flags: 0)")

  def test_any(self):
    comp = Any(1,2.3,str)
    self.assertTrue( comp.test(1) )
    self.assertTrue( comp.test(2.3) )
    self.assertFalse( comp.test(4) )
  
  def test_any_repr(self):
    comp = Any(1,2,3,str)
    self.assertEquals(repr(comp), "Any([1, 2, 3, IsA(str)])")
  
  def test_in(self):
    comp = In(['foo', 'bar'])
    self.assertTrue( comp.test('foo') )
    self.assertTrue( comp.test('bar') )
    self.assertFalse( comp.test('none') )
  
  def test_in_repr(self):
    comp = In(['foo', 'bar'])
    self.assertEqual(repr(comp), "In(['foo', 'bar'])")

  def test_contains(self):
    comp = Contains('foo')
    self.assertTrue( comp.test('foobar') )
    self.assertTrue( comp.test(['foo','bar']) )
    self.assertTrue( comp.test({'foo':'bar'}) )
    self.assertFalse( comp.test('feet') )
  
  def test_contains_repr(self):
    comp = Contains("foo")
    self.assertEqual(repr(comp), "Contains('foo')")

  def test_all(self):
    comp = All(IsA(bytearray), Equals('foo'))
    self.assertTrue( comp.test(bytearray('foo')) )
    self.assertFalse( comp.test('foo') )
    self.assertEquals( 'foo', bytearray('foo') )
  
  def test_all_repr(self):
    comp = All(IsA(bytearray), Equals('foobar'))
    self.assertEqual(repr(comp), "All([IsA(bytearray), 'foobar'])")

  def test_not(self):
    comp = Not( Any(1,3) )
    self.assertTrue( comp.test(2) )
    self.assertFalse( comp.test(1) )
    self.assertFalse( comp.test(3) )
  
  def test_no_repr(self):
    comp = Not(Any(1,3))
    self.assertEqual(repr(comp), "Not([Any([1, 3])])")

  def test_function(self):
    r = [True,False]
    comp = Function(lambda arg: r[arg])
    self.assertTrue( comp.test(0) )
    self.assertFalse( comp.test(1) )
  
  def test_function_repr(self):
    func = lambda arg: True
    comp = Function(func)
    self.assertEqual(repr(comp), "Function(%s)" % str(func))

  def test_ignore(self):
    comp = Ignore()
    self.assertTrue( comp.test('srsly?') )
  
  def test_ignore_repr(self):
    comp = Ignore()
    self.assertEqual(repr(comp), "Ignore()")

  def test_variable(self):
    comp = Variable('foo')
    self.assertEquals( 0, len(Variable._cache) )
    self.assertTrue( comp.test('bar') )
    self.assertEquals( 1, len(Variable._cache) )
    self.assertTrue( comp.test('bar') )
    self.assertFalse( comp.test('bar2') )
    
    self.assertTrue( Variable('foo').test('bar') )
    self.assertFalse( Variable('foo').test('bar2') )
    self.assertEquals( 1, len(Variable._cache) )

    self.assertEquals( 'bar', comp.value )
    self.assertEquals( 'bar', Variable('foo').value )

    v = Variable('foo2')
    self.assertEquals( 1, len(Variable._cache) )
    v.test('dog')
    self.assertEquals( 'dog', v.value )
    self.assertEquals( 2, len(Variable._cache) )

    Variable.clear()
    self.assertEquals( 0, len(Variable._cache) )

  def test_variable_repr(self):
    v = Variable('foo')
    self.assertEquals( repr(v), "Variable('foo')" )

  def test_like_init(self):
    c = Like({'foo':'bar'})
    self.assertEquals( {'foo':'bar'}, c._src )

    c = Like(['foo', 'bar'])
    self.assertEquals( ['foo','bar'], c._src )

  def test_like_test(self):
    c = Like({'foo':'bar'})
    self.assertTrue( c.test({'foo':'bar'}) )
    self.assertTrue( c.test({'foo':'bar', 'cat':'dog'}) )
    self.assertFalse( c.test({'foo':'barf'}) )
    
    c = Like(['foo','bar'])
    self.assertTrue( c.test(['foo','bar']) )
    self.assertTrue( c.test(['foo','bar','cat','dog']) )
    self.assertFalse( c.test(['foo','barf']) )

  def test_like_repr(self):
    c = Like({'foo':'bar'})
    self.assertEquals( repr(c), "Like({'foo': 'bar'})" )
