'''
Tests for the mock object
'''

import unittest
import types
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
