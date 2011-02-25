'''
Tests for the sample module
'''

from chai import Chai
from samples import SampleBase, SampleChild

import unittest2 as unittest

class SampleBaseTest(Chai):

  def test_expects_bound_method(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1, 2).returns(12)
    self.assertEquals(12, obj.bound_method(1, 2))
  
  @unittest.skip("")
  def test_expects_class_method(self):
    obj = SampleBase()
    self.expect(obj.a_classmethod).returns(12)
    self.assertEquals(12, obj.a_classmethod())

    self.expect(SampleBase.a_classmethod).returns(100)
    self.assertEquals(100, SampleBase.a_classmethod())
