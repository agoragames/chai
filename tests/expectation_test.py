
import unittest
import types

from chai.stub import Stub
from chai.expectation import *
from chai.comparators import *

class ArgumentsExpectationRuleTest(unittest.TestCase):
  
  def test_validate_with_no_args(self):
    r = ArgumentsExpectationRule()
    self.assertTrue(r.validate())

  def test_validate_with_no_args_and_some_params(self):
    r = ArgumentsExpectationRule()
    self.assertFalse(r.validate('foo'))
    self.assertFalse(r.validate(foo='bar'))

  def test_validate_with_args(self):
    r = ArgumentsExpectationRule(1,2,2)
    self.assertTrue(r.validate(1,2,2))

    r = ArgumentsExpectationRule(1,1,1)
    self.assertFalse(r.validate(2,2,2))

  def test_validate_with_kwargs(self):
    r = ArgumentsExpectationRule(name="vitaly")
    self.assertTrue(r.validate(name="vitaly"))

    r = ArgumentsExpectationRule(name="vitaly")
    self.assertFalse(r.validate(name="aaron"))

  def test_validate_with_args_and_kwargs(self):
    r = ArgumentsExpectationRule(1, name="vitaly")
    self.assertTrue(r.validate(1, name="vitaly"))

    r = ArgumentsExpectationRule(1, name="vitaly")
    self.assertFalse(r.validate(1, name="aaron"))

  def test_validate_with_args_that_are_different_length(self):
    r = ArgumentsExpectationRule(1)
    self.assertFalse(r.validate(1,1))

  def test_validate_with_kwargs_that_are_different(self):
    r = ArgumentsExpectationRule(name='vitaly')
    self.assertFalse(r.validate(age=837))
    self.assertFalse(r.validate(name='vitaly', age=837))

class ExpectationRule(unittest.TestCase):

  def setUp(self):
    self.stub = Stub(object)
  
  def test_default_expectation(self):
    exp = Expectation(self.stub)
    self.assertFalse(exp.closed())
    self.assertTrue(exp.match())
  
  def test_match_with_args(self):
    exp = Expectation(self.stub)
    exp.args(1, 2 ,3)
    
    self.assertTrue(exp.match(1,2,3))
  
  def test_match_with_kwargs(self):
    exp = Expectation(self.stub)
    exp.args(name="vitaly")
    
    self.assertTrue(exp.match(name="vitaly"))

  def test_match_with_both_args_and_kwargs(self):
    exp = Expectation(self.stub)
    exp.args(1, name="vitaly")
    
    self.assertTrue(exp.match(1, name="vitaly"))

  def test_match_with_any_args(self):
    exp = Expectation(self.stub)
    self.assertTrue( exp._any_args )
    self.assertTrue( exp is exp.any_args() )
    self.assertTrue( exp._any_args )

    self.assertTrue( exp.match() )
    self.assertTrue( exp.match('foo') )
    self.assertTrue( exp.match('bar', hello='world') )

  def test_times(self):
    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.times(3) )
    self.assertEquals( 3, exp._min_count )
    self.assertEquals( 3, exp._max_count )
  
  def test_at_least_once(self):
    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.at_least_once() )
    exp.test()
    self.assertTrue(exp.closed(with_counts=True))

  def test_at_least(self):
    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.at_least(10) )
    for x in range(10):
      exp.test()
    self.assertTrue(exp.closed(with_counts=True))

  def test_at_most_once(self):
    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.args(1).at_most_once() )
    exp.test(1)
    self.assertTrue(exp.closed(with_counts=True))

  def test_at_most(self):
    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.args(1).at_most(10) )
    for x in range(10):
      exp.test(1)
    self.assertTrue(exp.closed(with_counts=True))
  
  def test_once(self):
    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.args(1).once() )
    exp.test(1)
    self.assertTrue(exp.closed())

  def test_any_order(self):
    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.any_order().times(1) )
    self.assertFalse( exp.closed() )
    exp.close()
    self.assertFalse( exp.closed() )
    self.assertFalse( exp.closed(with_counts=True) )
    exp.test()
    self.assertTrue( exp.closed() )
    self.assertTrue( exp.closed(with_counts=True) )

  def test_any_order_with_no_max(self):
    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.any_order().at_least_once() )
    self.assertFalse( exp.closed() )
    exp.close()
    self.assertFalse( exp.closed() )
    self.assertFalse( exp.closed(with_counts=True) )
    exp.test()
    self.assertFalse( exp.closed() )
    self.assertTrue( exp.closed(with_counts=True) )

  def test_side_effect(self):
    called = []
    def effect(foo=called):
      foo.append('foo')

    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.side_effect(effect) )
    exp.test()
    self.assertEquals( ['foo'], called )

  def test_side_effect_with_args(self):
    called = []
    def effect(a, b=None):
      if a=='a' and b=='c':
        called.append('foo')

    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.side_effect(effect, 'a', b='c') )
    exp.test()
    self.assertEquals( ['foo'], called )

  def test_side_effect_with_passed_args(self):
    called = []
    def effect(a, b=None):
      if a=='a' and b=='c':
        called.append('foo')

    exp = Expectation(self.stub)
    exp.args('a', b='c')
    self.assertEquals( exp, exp.side_effect(effect) )
    exp.test('a', b='c')
    self.assertEquals( ['foo'], called )

  def test_side_effect_with_an_exception(self):
    called = []
    def effect(foo=called):
      foo.append('foo')
    class Zono(Exception): pass

    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.side_effect(effect).raises(Zono) )
    self.assertRaises( Zono, exp.test )
    self.assertEquals( ['foo'], called )

  def test_teardown(self):
    called = []
    class notastub(object):
      expectations = []
      def teardown(self, foo=called):
        foo.append( 'foo' )

    exp = Expectation( notastub() )
    exp.teardown()
    exp.test()
    self.assertEquals( ['foo'], called )

  def test_closed(self):
    exp = Expectation(self.stub)
    exp.args(1).times(1)
    exp.test(1)
    self.assertTrue(exp.closed())

  def test_closed_with_count(self):
    exp = Expectation(self.stub)
    exp.args(1).at_least(1)
    exp.test(1)
    self.assertTrue(exp.closed(with_counts=True))

  def test_close(self):
    exp = Expectation(self.stub)
    exp.test()
    exp.close()
    self.assertTrue(exp.closed())

  def test_return_value_with_value(self):
    exp = Expectation(self.stub)
    exp.returns(123)
    
    self.assertEquals(exp.test(), 123)

  def test_return_value_with_variable(self):
    exp = Expectation(self.stub)
    var = Variable('test')
    Variable._cache['test'] = 123
    exp.returns( var )
    
    self.assertEquals(exp.test(), 123)
    Variable.clear()

  def test_return_value_with_variable_in_tuple(self):
    exp = Expectation(self.stub)
    var = Variable('test')
    Variable._cache['test'] = 123
    exp.returns( (var,'foo') )
    
    self.assertEquals(exp.test(), (123,'foo'))
    Variable.clear()

  def test_with_returns_return_value(self):
    exp = Expectation(self.stub)
    with exp.returns(123) as num:
      self.assertEquals(num, 123)

  def test_with_raises_exceptions(self):
    exp = Expectation(self.stub)

    # pre-2.7 compatible
    def foo():
      with exp.returns(123) as num:
        raise Exception("FAIL!")
    self.assertRaises(Exception, foo)

  def test_return_value_with_exception_class(self): 
    class CustomException(Exception): pass
    
    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.raises(CustomException) )
    
    self.assertRaises(CustomException, exp.test)

  def test_return_value_with_exception_instance(self): 
    class CustomException(Exception): pass
    
    exp = Expectation(self.stub)
    self.assertEquals( exp, exp.raises(CustomException()) )
    
    self.assertRaises(CustomException, exp.test)
  
