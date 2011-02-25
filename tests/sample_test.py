'''
Tests for the sample module
'''

from chai import Chai
from stub import stub
from exception import *
import samples
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

  def test_expects_bound_method_can_be_used_for_iterative_testing(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1, 2).returns(12)
    self.assertEquals(12, obj.bound_method(1, 2))
    self.assertRaises(UnexpectedCall, obj.bound_method)

    self.expect(obj.bound_method).args(1, 4).returns(1100)
    self.assertEquals(1100, obj.bound_method(1, 4))

  def test_stub_bound_method_raises_unexpectedcall(self):
    obj = SampleBase()
    self.stub(obj.bound_method)
    self.assertRaises(UnexpectedCall, obj.bound_method)

  def test_expect_unbound_method_acts_as_any_instance(self):
    self.expect( SampleBase.bound_method ).args('hello').returns('world')
    self.expect( SampleBase.bound_method ).args('hello').returns('mars')

    obj1 = SampleBase()
    obj2 = SampleBase()
    self.assertEquals( 'world', obj2.bound_method('hello') )
    self.assertEquals( 'mars', obj1.bound_method('hello') )
    self.assertRaises(UnexpectedCall, obj2.bound_method)

  def test_stub_unbound_method_acts_as_no_instance(self):
    self.stub( SampleBase.bound_method )

    obj1 = SampleBase()
    obj2 = SampleBase()
    self.assertRaises(UnexpectedCall, obj2.bound_method)
    self.assertRaises(UnexpectedCall, obj1.bound_method)
  
  def test_expects_class_method(self):
    self.expect(SampleBase.a_classmethod).returns(12)
    self.assertEquals(12, SampleBase.a_classmethod())

    obj = SampleBase()
    self.expect(SampleBase.a_classmethod).returns(100)
    self.assertEquals(100, obj.a_classmethod())

  def test_stub_class_method(self):
    self.stub(SampleBase.a_classmethod)
    self.assertRaises(UnexpectedCall, SampleBase.a_classmethod)

    obj = SampleBase()
    self.assertRaises(UnexpectedCall, obj.a_classmethod)

  def test_expect_callback(self):
    obj = SampleBase()
    self.expect(obj.callback_target)
    obj.callback_source()

  def test_add_to_list_with_mock_object(self):
    obj = SampleBase()
    obj._deque = self.mock()
    self.expect( obj._deque.append ).args('value')
    obj.add_to_list('value')

  def test_add_to_list_with_module_mock_object(self):
    self.mock( samples, 'deque' )
    deq = self.mock()
    self.expect( samples.deque.__call__ ).returns( deq )
    self.expect( deq.append ).args('value')

    obj = SampleBase()
    obj.add_to_list('value')

class SampleChildTest(Chai):

  def test_stub_base_class_expect_child_classmethod(self):
    self.stub(SampleBase.a_classmethod)
    self.expect(SampleChild.a_classmethod)

    SampleChild.a_classmethod()
