'''
Tests for the mock object
'''

import unittest
import types

from chai.comparators import *
from chai.mock import Mock
from chai.exception import UnexpectedCall
from chai.stub import stub

class MockTest(unittest.TestCase):

 # def test_get_attribute_creates_a_new_method(self):
 #   m = Mock()
 #   self.assertTrue( isinstance(m.foo, types.MethodType) )
  def test_get_attribute_creates_a_mock_method(self):
    m = Mock()
    self.assertTrue( isinstance(m.foo, Mock) )
    self.assertFalse( m.foo is m )

  def test_get_attribute_caches_auto_methods(self):
    m = Mock()
    self.assertTrue( m.foo is m.foo )

  def test_get_attribute_supports_multiple_depths(self):
    m = Mock()
    self.assertTrue( isinstance(m.foo.bar, Mock) )

  def test_get_attribute_auto_method_raises_unexpectedcall_when_unstubbed(self):
    m = Mock()
    self.assertRaises( UnexpectedCall, m.foo )

  def test_get_attribute_auto_method_raises_unexpectedcall_when_stubbed(self):
    m = Mock()
    stub( m.foo )
    self.assertRaises( UnexpectedCall, m.foo )

  def test_get_attribute_auto_method_not_raises_unexpectedcall_when_stubbed(self):
    m = Mock()
    stub(m.foo).expect().returns('success')
    self.assertEquals( 'success', m.foo() )

  def test_get_attribute_auto_method_not_raises_unexpectedcall_multiple_depths(self):
    m = Mock()
    stub(m.foo.bar).expect().returns('success')
    self.assertEquals( 'success', m.foo.bar() )

  def test_get_attribute_does_not_overwrite_existing_attr(self):
    m = Mock()
    m.foo = 42
    self.assertEquals( 42, m.foo )

  def test_call_raises_unexpectedcall_when_unstubbed(self):
    m = Mock()
    self.assertRaises( UnexpectedCall, m )

  def test_call_not_raises_unexpectedcall_when_stubbed(self):
    m = Mock()
    stub(m).expect().returns('success')
    self.assertEquals( 'success', m() )

  def test_nonzero_returns_true_when_unstubbed(self):
    m = Mock()
    self.assertTrue( m.__nonzero__() )

  def test_nonzero_when_stubbed(self):
    m = Mock()
    stub(m.__nonzero__).expect().returns(False)
    self.assertFalse( m.__nonzero__() )

  def test_container_interface_when_unstubbed(self):
    m = Mock()
    self.assertRaises( UnexpectedCall, len, m )
    self.assertRaises( UnexpectedCall, m.__getitem__, 'foo' )
    self.assertRaises( UnexpectedCall, m.__setitem__, 'foo', 'bar' )
    self.assertRaises( UnexpectedCall, m.__delitem__, 'foo' )
    self.assertRaises( UnexpectedCall, iter, m )
    self.assertRaises( UnexpectedCall, reversed, m )
    self.assertRaises( UnexpectedCall, m.__contains__, 'foo' )
    self.assertRaises( UnexpectedCall, m.__getslice__, 'i', 'j')
    self.assertRaises( UnexpectedCall, m.__setslice__, 'i', 'j', 'foo')
    self.assertRaises( UnexpectedCall, m.__delslice__, 'i', 'j')

  def test_container_interface_when_stubbed(self):
    m = Mock()
    i = iter([1,2,3])

    stub( m.__len__ ).expect().returns( 42 )
    stub( m.__getitem__ ).expect().args('foo').returns('getitem')
    stub( m.__setitem__ ).expect().args('foo', 'bar')
    stub( m.__delitem__ ).expect().args('foo')
    stub( m.__iter__ ).expect().returns( i )
    stub( m.__reversed__ ).expect().returns( 'backwards' )
    stub( m.__contains__ ).expect().args('foo').returns( True )

    self.assertEquals( 42, len(m) )
    self.assertEquals( 'getitem', m['foo'] )
    m['foo']='bar'
    del m['foo']
    self.assertEquals( i, iter(m) )
    self.assertEquals( 'backwards', reversed(m) )
    self.assertEquals( True, 'foo' in m )

  def test_context_manager_interface_when_unstubbed(self):
    m = Mock()

    def cm():
      with m:
        pass

    self.assertRaises( UnexpectedCall, cm )

  def test_context_manager_interface_when_stubbed(self):
    m = Mock()
    exc = Exception('fail')

    def cm_noraise():
      with m: pass

    def cm_raise():
      with m:
        raise exc

    stub( m.__enter__ ).expect().times(2)
    stub( m.__exit__ ).expect().args( None, None, None )
    stub( m.__exit__ ).expect().args( Is(Exception), exc, types.TracebackType )

    cm_noraise()
    self.assertRaises( Exception, cm_raise )
