'''
Tests for the sample module
'''

from chai import Chai
from stub import stub
from samples import SampleBase, SampleChild

import unittest2 as unittest

class SampleBaseTest(Chai):

  def test_expects_bound_method(self):
    obj = SampleBase()
    obj.bound_method = stub(obj.bound_method)
    self.expect(obj.bound_method).args(1, 2).returns(12)
    self.assertEquals(12, obj.bound_method(1, 2))
  
  def test_expects_class_method(self):
    obj = SampleBase()
    obj.a_classmethod = stub(obj.a_classmethod)
    self.expect(obj.a_classmethod).returns(12)
    self.assertEquals(12, obj.a_classmethod())

    SampleBase.a_classmethod = stub(SampleBase.a_classmethod)
    self.expect(SampleBase.a_classmethod).returns(100)
    self.assertEquals(100, SampleBase.a_classmethod())
