'''
Tests for the sample module
'''

from chai import Chai
from stub import stub
from samples import SampleBase, SampleChild

import unittest2 as unittest

class CustomException(Exception): pass

class SampleBaseTest(Chai):

  def test_expects_bound_method_returns(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1, 2).returns(12)
    self.assertEquals(12, obj.bound_method(1, 2))

    self.expect(obj.bound_method).args(1, 4).returns(1100)
    self.assertEquals(1100, obj.bound_method(1, 4))

  def test_expects_bound_method_raises(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1, 2).raises(CustomException)
    self.assertRaises(CustomException, obj.bound_method, 1, 2)

    self.expect(obj.bound_method).args(1, 2).raises(CustomException())
    self.assertRaises(CustomException, obj.bound_method, 1, 2)

  def test_expects_class_method(self):
    obj = SampleBase()
    self.expect(obj.a_classmethod).returns(12)
    self.assertEquals(12, obj.a_classmethod())

    self.expect(SampleBase.a_classmethod).returns(100)
    self.assertEquals(100, SampleBase.a_classmethod())
