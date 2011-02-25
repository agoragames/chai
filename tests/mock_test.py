'''
Tests for the mock object
'''

import unittest
from mock import Mock
from stub import *

class MockTest(unittest.TestCase):

  def test_get_attribute_stubs_a_new_method(self):
    m = Mock()
    self.assertTrue( isinstance(m.foo, StubMethod) )
  
  def test_get_attribute_caches_stub(self):
    m = Mock()
    s = m.foo
    self.assertEquals( s, m.foo )
