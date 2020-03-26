"""
Tests for the sample module
"""

import os
import unittest
import sys

from chai import Chai
from chai.stub import stub
from chai.exception import *
import tests.samples as samples
from tests.samples import SampleBase, SampleChild

try:
    IS_PYPY = sys.subversion[0] == 'PyPy'
except AttributeError:
    IS_PYPY = False


class CustomException(Exception):
    pass


class SampleModuleTest(Chai):

  def test_mod_func_2_as_obj_name(self):
    expect(samples, 'mod_func_1').args(42, foo='bar')
    samples.mod_func_2(42, foo='bar')

  def test_mod_func_2_as_obj_ref(self):
    expect(samples.mod_func_1).args(42, foo='bar')
    samples.mod_func_2(42, foo='bar')


class SampleBaseTest(Chai):

  def test_expects_property(self):
    obj = SampleBase()
    expect(obj, 'prop').returns("property value")
    assert_equals("property value", obj.prop)

  def test_expects_on_builtin_function(self):
    # NOTE: os module is a good example where it binds from another
    # (e.g. posix), so it has to use the named reference or else it
    # stubs the original module
    expect(os, 'remove').args('foo').returns('ok')
    assert_equals('ok', os.remove('foo'))

  def test_expects_bound_method_returns(self):
    obj = SampleBase()
    expect(obj.bound_method).args(1, 2).returns(12)
    assert_equals(12, obj.bound_method(1, 2))

    expect(obj.bound_method).args(1, 4).returns(1100)
    assert_equals(1100, obj.bound_method(1, 4))

  def test_expects_bound_method_at_least_with_other_expectation_and_no_anyorder(self):
    obj = SampleBase()
    expect(obj.bound_method).args(1, 2).returns(12).at_least(2)
    assert_equals(12, obj.bound_method(1, 2))
    assert_equals(12, obj.bound_method(1, 2))

    expect(obj.bound_method).args(1, 3).returns(100)
    assert_equals(100, obj.bound_method(1, 3))

    assert_raises(UnexpectedCall, obj.bound_method, 1, 2)

  def test_expects_bound_method_at_least_with_other_expectation_and_anyorder(self):
    obj = SampleBase()
    expect(obj.bound_method).args(1, 2).returns(12).at_least(2).any_order()
    assert_equals(12, obj.bound_method(1, 2))
    assert_equals(12, obj.bound_method(1, 2))

    expect(obj.bound_method).args(1, 3).returns(100)
    assert_equals(100, obj.bound_method(1, 3))

    assert_equals(12, obj.bound_method(1, 2))

  def test_expects_bound_method_at_least_as_last_expectation(self):
    obj = SampleBase()
    expect(obj.bound_method).args(1, 2).returns(12).at_least(3)
    assert_equals(12, obj.bound_method(1, 2))
    assert_equals(12, obj.bound_method(1, 2))
    assert_equals(12, obj.bound_method(1, 2))
    assert_equals(12, obj.bound_method(1, 2))

  def test_expects_bound_method_at_most(self):
    obj = SampleBase()
    expect(obj.bound_method).args(1, 2).returns(12).at_most(3)
    assert_equals(12, obj.bound_method(1, 2))
    assert_equals(12, obj.bound_method(1, 2))
    obj.bound_method(1, 2)
    assert_raises(UnexpectedCall, obj.bound_method, 1, 2)

  def tests_expects_bound_method_any_order_with_fixed_maxes(self):
    obj = SampleBase()
    expect(obj.bound_method).args(1).returns(2).any_order()
    expect(obj.bound_method).args(3).returns(4).any_order()
    assert_equals(4, obj.bound_method(3))
    assert_equals(2, obj.bound_method(1))
    assert_raises(UnexpectedCall, obj.bound_method, 1)

  def tests_expects_bound_method_any_order_with_mins(self):
    obj = SampleBase()
    expect(obj.bound_method).args(1).returns(2).any_order().at_least_once()
    expect(obj.bound_method).args(3).returns(4).any_order().at_least_once()
    assert_equals(4, obj.bound_method(3))
    assert_equals(2, obj.bound_method(1))
    assert_equals(4, obj.bound_method(3))
    assert_equals(2, obj.bound_method(1))
    assert_equals(2, obj.bound_method(1))
    assert_equals(4, obj.bound_method(3))
    assert_equals(2, obj.bound_method(1))

  def test_expects_any_order_without_count_modifiers(self):
    obj = SampleBase()
    expect(obj.bound_method).args(3).returns(4)
    expect(obj.bound_method).args(1).returns(2).any_order()
    expect(obj.bound_method).args(3).returns(4)
    assert_equals(4, obj.bound_method(3))
    assert_equals(4, obj.bound_method(3))
    assert_equals(2, obj.bound_method(1))

  def test_expects_bound_method_raises(self):
    obj = SampleBase()
    expect(obj.bound_method).args(1, 2).raises(CustomException)
    assert_raises(CustomException, obj.bound_method, 1, 2)

    expect(obj.bound_method).args(1, 2).raises(CustomException())
    assert_raises(CustomException, obj.bound_method, 1, 2)

  def test_expects_bound_method_can_be_used_for_iterative_testing(self):
    obj = SampleBase()
    expect(obj.bound_method).args(1, 2).returns(12)
    assert_equals(12, obj.bound_method(1, 2))
    assert_raises(UnexpectedCall, obj.bound_method)

    expect(obj.bound_method).args(1, 4).returns(1100)
    assert_equals(1100, obj.bound_method(1, 4))

  def test_stub_bound_method_raises_unexpectedcall(self):
    obj = SampleBase()
    stub(obj.bound_method)
    assert_raises(UnexpectedCall, obj.bound_method)

  def test_expect_bound_method_with_equals_comparator(self):
    obj = SampleBase()
    expect(obj.bound_method).args(equals(42))
    obj.bound_method(42)
    assert_raises(UnexpectedCall, obj.bound_method, 32)

  def test_expect_bound_method_with_is_a_comparator(self):
    obj = SampleBase()
    expect(obj.bound_method).args(is_a(int))
    obj.bound_method(42)
    assert_raises(UnexpectedCall, obj.bound_method, '42')

  def test_expect_bound_method_with_anyof_comparator(self):
    obj = SampleBase()
    expect(obj.bound_method).times(4).args(
      any_of(int, 3.14, 'hello', is_a(list)))
    obj.bound_method(42)
    obj.bound_method(3.14)
    obj.bound_method('hello')
    obj.bound_method([1, 2, 3])
    assert_raises(UnexpectedCall, obj.bound_method, '42')

  def test_expect_bound_method_with_allof_comparator(self):
    obj = SampleBase()
    expect(obj.bound_method).args(all_of(length(5), 'hello'))
    obj.bound_method('hello')

    expect(obj.bound_method).args(all_of(length(3), 'hello')).at_least(0)
    assert_raises(UnexpectedCall, obj.bound_method, 'hello')

  def test_expect_bound_method_with_notof_comparator(self):
    obj = SampleBase()
    expect(obj.bound_method).args(not_of(any_of(float, int)))
    obj.bound_method('hello')

  def test_expect_bound_method_with_notof_comparator_using_types(self):
    obj = SampleBase()
    expect(obj.bound_method).args(not_of(float, int))
    obj.bound_method('hello')

  def test_expect_unbound_method_acts_as_any_instance(self):
    expect(SampleBase, 'bound_method').args('hello').returns('world')
    expect(SampleBase, 'bound_method').args('hello').returns('mars')

    obj1 = SampleBase()
    obj2 = SampleBase()
    assert_equals('world', obj2.bound_method('hello'))
    assert_equals('mars', obj1.bound_method('hello'))
    assert_raises(UnexpectedCall, obj2.bound_method)

  def test_stub_unbound_method_acts_as_no_instance(self):
    stub(SampleBase, 'bound_method')

    obj1 = SampleBase()
    obj2 = SampleBase()
    assert_raises(UnexpectedCall, obj2.bound_method)
    assert_raises(UnexpectedCall, obj1.bound_method)

  def test_expects_class_method(self):
    expect(SampleBase.a_classmethod).returns(12)
    assert_equals(12, SampleBase.a_classmethod())

    obj = SampleBase()
    expect(SampleBase.a_classmethod).returns(100)
    assert_equals(100, obj.a_classmethod())

  def test_stub_class_method(self):
    stub(SampleBase.a_classmethod)
    assert_raises(UnexpectedCall, SampleBase.a_classmethod)

    obj = SampleBase()
    assert_raises(UnexpectedCall, obj.a_classmethod)

  def test_expect_callback(self):
    obj = SampleBase()
    expect(obj.callback_target)
    obj.callback_source()

  def test_add_to_list_with_mock_object(self):
    obj = SampleBase()
    obj._deque = mock()
    expect(obj._deque.append).args('value')
    obj.add_to_list('value')

  def test_add_to_list_with_module_mock_object(self):
    mock(samples, 'deque')
    deq = mock()
    expect(samples.deque.__call__).returns(deq)
    expect(deq.append).args('value')

    obj = SampleBase()
    obj.add_to_list('value')

  def test_regex_comparator(self):
    obj = SampleBase()
    expect(obj.bound_method).args(matches("name$")).returns(100)
    assert_equals(obj.bound_method('first_name'), 100)

  def test_ignore_arg(self):
    obj = SampleBase()
    expect(obj.bound_method).args(ignore_arg()).returns(100)
    assert_equals(obj.bound_method('first_name'), 100)

  def test_function_comparator(self):
    obj = SampleBase()
    expect(obj.bound_method).args(func(lambda arg: arg > 10)).returns(100)
    assert_equals(obj.bound_method(100), 100)

  def test_in_comparator(self):
    obj = SampleBase()
    expect(obj.bound_method).args(contains('name')).returns(100).at_most(3)
    assert_equals(obj.bound_method(['name', 'age']), 100)
    assert_equals(obj.bound_method({'name': 'vitaly'}), 100)
    assert_equals(obj.bound_method('lasfs-name-asfsad'), 100)

  def test_almost_equals_comparator(self):
    obj = SampleBase()
    expect(obj.bound_method).args(almost_equals(10.1234, 2)).returns(100)
    assert_equals(obj.bound_method(10.12), 100)

  def test_is_comparator(self):
    obj = SampleBase()
    expect(obj.bound_method).args(is_arg(obj)).returns(100)
    assert_equals(obj.bound_method(obj), 100)

  def test_var_comparator(self):
    obj = SampleBase()
    expect(obj.add_to_list).args(var('value1'))
    expect(obj.add_to_list).args(var('value2'))
    expect(obj.add_to_list).args(var('value3')).at_least_once()

    obj.add_to_list('v1')
    obj.add_to_list('v2')
    obj.add_to_list('v3')
    obj.add_to_list('v3')
    self.assertRaises(UnexpectedCall, obj.add_to_list, 'v3a')

    assert_equals('v1', var('value1').value)
    assert_equals('v2', var('value2').value)
    assert_equals('v3', var('value3').value)

  def test_spy(self):
    spy(SampleBase)
    obj = SampleBase()
    assert_true(isinstance(obj, SampleBase))

    spy(obj.add_to_list)
    obj.add_to_list('v1')
    assert_equals(['v1'], list(obj._deque))

    spy(obj.add_to_list).args(var('value2'))
    obj.add_to_list('v2')
    assert_equals(['v1', 'v2'], list(obj._deque))
    assert_equals('v2', var('value2').value)

    data = {'foo': 'bar'}

    def _sfx(_data):
      _data['foo'] = 'bug'

    spy(obj.add_to_list).side_effect(_sfx, data)
    obj.add_to_list('v3')
    assert_equals(['v1', 'v2', 'v3'], list(obj._deque))
    assert_equals({'foo': 'bug'}, data)

    capture = [0]

    def _return_spy(_deque):
      capture.extend(_deque)

    spy(obj.add_to_list).spy_return(_return_spy)
    obj.add_to_list('v4')
    assert_equals([0, 'v1', 'v2', 'v3', 'v4'], capture)

    with assert_raises(UnsupportedModifier):
        spy(obj.add_to_list).times(0).returns(3)
    with assert_raises(UnsupportedModifier):
        spy(obj.add_to_list).times(0).raises(Exception('oops'))

  @unittest.skipIf(IS_PYPY, "can't spy on wrapper-descriptors in PyPy")
  def test_spy_on_method_wrapper(self):
    obj = SampleBase()
    spy(SampleBase, '__hash__')
    dict()[obj] = 'hello world'


class SampleChildTest(Chai):

  def test_stub_base_class_expect_child_classmethod(self):
    stub(SampleBase.a_classmethod)
    expect(SampleChild.a_classmethod)

    SampleChild.a_classmethod()
