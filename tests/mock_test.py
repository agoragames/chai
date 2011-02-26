'''
Tests for the mock object
'''

import unittest
import types
from chai.mock import Mock

class MockTest(unittest.TestCase):

  def test_get_attribute_stubs_a_new_method(self):
    m = Mock()
    self.assertTrue( isinstance(m.foo, types.MethodType) )
  
  def test_get_attribute_caches_stub(self):
    m = Mock()
    s = m.foo
    self.assertEquals( s, m.foo )
