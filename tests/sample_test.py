'''
Tests for the sample module
'''

from chai import Chai
from chai.stub import stub
from chai.exception import *
import samples
from samples import SampleBase, SampleChild

import unittest2 as unittest

class CustomException(Exception): pass

class SampleBaseTest(Chai):

  def test_expects_bound_method_returns(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1, 2).returns(12)
    self.assert_equals(12, obj.bound_method(1, 2))

    self.expect(obj.bound_method).args(1, 4).returns(1100)
    self.assert_equals(1100, obj.bound_method(1, 4))

  def test_expects_bound_method_at_least_with_other_expectation(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1, 2).returns(12).at_least(3)
    self.assert_equals(12, obj.bound_method(1, 2))
    self.assert_equals(12, obj.bound_method(1, 2))

    self.expect(obj.bound_method).args(1, 3).returns(100)
    self.assert_equals(100, obj.bound_method(1, 3))
    
    self.assert_equals(12, obj.bound_method(1, 2))

  def test_expects_bound_method_at_least_as_last_expectation(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1, 2).returns(12).at_least(3)
    self.assert_equals(12, obj.bound_method(1, 2))
    self.assert_equals(12, obj.bound_method(1, 2))
    self.assert_equals(12, obj.bound_method(1, 2))
    self.assert_equals(12, obj.bound_method(1, 2))

  def test_expects_bound_method_at_most(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1, 2).returns(12).at_most(3)
    self.assert_equals(12, obj.bound_method(1, 2))
    self.assert_equals(12, obj.bound_method(1, 2))
    obj.bound_method(1, 2)
    self.assert_raises(UnexpectedCall, obj.bound_method, 1, 2)

  def tests_expects_bound_method_any_order_with_fixed_maxes(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1).returns(2).any_order()
    self.expect(obj.bound_method).args(3).returns(4).any_order()
    self.assert_equals(4, obj.bound_method(3) )
    self.assert_equals(2, obj.bound_method(1) )
    self.assert_raises(UnexpectedCall, obj.bound_method, 1)

  def tests_expects_bound_method_any_order_with_mins(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1).returns(2).any_order().at_least_once()
    self.expect(obj.bound_method).args(3).returns(4).any_order().at_least_once()
    self.assert_equals(4, obj.bound_method(3) )
    self.assert_equals(2, obj.bound_method(1) )
    self.assert_equals(4, obj.bound_method(3) )
    self.assert_equals(2, obj.bound_method(1) )
    self.assert_equals(2, obj.bound_method(1) )
    self.assert_equals(4, obj.bound_method(3) )
    self.assert_equals(2, obj.bound_method(1) )

  def test_expects_bound_method_raises(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1, 2).raises(CustomException)
    self.assert_raises(CustomException, obj.bound_method, 1, 2)

    self.expect(obj.bound_method).args(1, 2).raises(CustomException())
    self.assert_raises(CustomException, obj.bound_method, 1, 2)

  def test_expects_bound_method_can_be_used_for_iterative_testing(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(1, 2).returns(12)
    self.assert_equals(12, obj.bound_method(1, 2))
    self.assert_raises(UnexpectedCall, obj.bound_method)

    self.expect(obj.bound_method).args(1, 4).returns(1100)
    self.assert_equals(1100, obj.bound_method(1, 4))

  def test_stub_bound_method_raises_unexpectedcall(self):
    obj = SampleBase()
    self.stub(obj.bound_method)
    self.assert_raises(UnexpectedCall, obj.bound_method)
  
  def test_expect_bound_method_with_equals_comparator(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args( self.equals(42) )
    obj.bound_method( 42 )
    self.assert_raises(UnexpectedCall, obj.bound_method, 32 )

  def test_expect_bound_method_with_instanceof_comparator(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args( self.instance_of(int) )
    obj.bound_method( 42 )
    self.assert_raises(UnexpectedCall, obj.bound_method, '42' )
  
  def test_expect_bound_method_with_anyof_comparator(self):
    obj = SampleBase()
    self.expect(obj.bound_method).times(4).args( 
      self.any_of(int,3.14,'hello',self.instance_of(list)) )
    obj.bound_method( 42 )
    obj.bound_method( 3.14 )
    obj.bound_method( 'hello' )
    obj.bound_method( [1,2,3] )
    self.assert_raises(UnexpectedCall, obj.bound_method, '42' )

  def test_expect_bound_method_with_allof_comparator(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args( self.all_of(bytearray,'hello') )
    obj.bound_method( bytearray('hello') )
    self.assert_raises(UnexpectedCall, obj.bound_method, 'hello' )
  
  def test_expect_bound_method_with_notof_comparator(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args( self.not_of(self.any_of(float,int)) )
    obj.bound_method( 'hello' )

  def test_expect_bound_method_with_notof_comparator_using_types(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args( self.not_of(float,int) )
    obj.bound_method( 'hello' )
    
  def test_expect_unbound_method_acts_as_any_instance(self):
    self.expect( SampleBase.bound_method ).args('hello').returns('world')
    self.expect( SampleBase.bound_method ).args('hello').returns('mars')

    obj1 = SampleBase()
    obj2 = SampleBase()
    self.assert_equals( 'world', obj2.bound_method('hello') )
    self.assert_equals( 'mars', obj1.bound_method('hello') )
    self.assert_raises(UnexpectedCall, obj2.bound_method)

  def test_stub_unbound_method_acts_as_no_instance(self):
    self.stub( SampleBase.bound_method )

    obj1 = SampleBase()
    obj2 = SampleBase()
    self.assert_raises(UnexpectedCall, obj2.bound_method)
    self.assert_raises(UnexpectedCall, obj1.bound_method)
  
  def test_expects_class_method(self):
    self.expect(SampleBase.a_classmethod).returns(12)
    self.assert_equals(12, SampleBase.a_classmethod())

    obj = SampleBase()
    self.expect(SampleBase.a_classmethod).returns(100)
    self.assert_equals(100, obj.a_classmethod())

  def test_stub_class_method(self):
    self.stub(SampleBase.a_classmethod)
    self.assert_raises(UnexpectedCall, SampleBase.a_classmethod)

    obj = SampleBase()
    self.assert_raises(UnexpectedCall, obj.a_classmethod)

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
  
  def test_regex_comparator(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(self.matches("name$")).returns(100)
    self.assert_equals(obj.bound_method('first_name'), 100)

  def test_regex_comparator(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(self.matches("name$")).returns(100)
    self.assert_equals(obj.bound_method('first_name'), 100)

  def test_ignore_arg(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(self.ignore_arg()).returns(100)
    self.assert_equals(obj.bound_method('first_name'), 100)

  def test_function_comparator(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(self.func(lambda arg: arg > 10)).returns(100)
    self.assert_equals(obj.bound_method(100), 100)

  def test_in_comparator(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(self.contains('name')).returns(100).at_most(3)
    self.assert_equals(obj.bound_method(['name', 'age']), 100)
    self.assert_equals(obj.bound_method({'name' : 'vitaly'}), 100)
    self.assert_equals(obj.bound_method('lasfs-name-asfsad'), 100)

  def test_almost_equals_comparator(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(self.almost_equals(10.1234, 2)).returns(100)
    self.assert_equals(obj.bound_method(10.12), 100)

  def test_is_comparator(self):
    obj = SampleBase()
    self.expect(obj.bound_method).args(self.is_arg(obj)).returns(100)
    self.assert_equals(obj.bound_method(obj), 100)

class SampleChildTest(Chai):

  def test_stub_base_class_expect_child_classmethod(self):
    self.stub(SampleBase.a_classmethod)
    self.expect(SampleChild.a_classmethod)

    SampleChild.a_classmethod()
