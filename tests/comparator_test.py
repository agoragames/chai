
import unittest

from chai.comparators import *

class ComparatorsTest(unittest.TestCase):

  def test_equals(self):
    comp = Equals(3)
    self.assertTrue( comp.test(3) )
    self.assertTrue( comp.test(3.0) )
    self.assertFalse( comp.test('3') )

  def test_instance_of(self):
    comp = InstanceOf(str)
    self.assertTrue( comp.test('foo') )
    self.assertFalse( comp.test(u'foo') )
    self.assertFalse( comp.test(bytearray('foo')) )
    
    comp = InstanceOf((str,int))
    self.assertTrue( comp.test('') )
    self.assertTrue( comp.test(42) )
    self.assertFalse( comp.test(3.14) )

  def test_is(self):
    class Test(object):
      def __eq__(self, other): return True

    obj1 = Test()
    obj2 = Test()
    comp = Is(obj1)
    self.assertEquals( obj1, obj2 )
    self.assertTrue( comp.test(obj1) )
    self.assertFalse( comp.test(obj2) )

  def test_almost_equal(self):
    comp = AlmostEqual(3.14159265, 3)
    self.assertTrue( comp.test(3.1416) )
    self.assertFalse( comp.test(3.14) )

  def test_contains(self):
    comp = Contains('foo')
    self.assertTrue( comp.test('foobar') )
    self.assertTrue( comp.test(['foo','bar']) )
    self.assertTrue( comp.test({'foo':'bar'}) )
    self.assertFalse( comp.test('feet') )

  def test_regex(self):
    comp = Regex('[wf][io]{2}')
    self.assertTrue( comp.test('fii') )
    self.assertTrue( comp.test('woo') )
    self.assertFalse( comp.test('fuu') )

  def test_any(self):
    comp = Any([1,2.3,str])
    self.assertTrue( comp.test(1) )
    self.assertTrue( comp.test(2.3) )
    self.assertFalse( comp.test(4) )

  def test_all(self):
    comp = All([InstanceOf(bytearray), Equals('foo')])
    self.assertTrue( comp.test(bytearray('foo')) )
    self.assertFalse( comp.test('foo') )
    self.assertEquals( 'foo', bytearray('foo') )

  def test_not(self):
    comp = Not([1,3])
    self.assertTrue( comp.test(2) )
    self.assertFalse( comp.test(1) )

  def test_function(self):
    r = [True,False]
    comp = Function(lambda arg: r[arg])
    self.assertTrue( comp.test(0) )
    self.assertFalse( comp.test(1) )

  def test_ignore(self):
    comp = Ignore()
    self.assertTrue( comp.test('srsly?') )
