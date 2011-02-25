
import unittest
import types

from expectation import *

class ArgumentsExpecationRuleTest(unittest.TestCase):
  
  def test_validate_with_no_args(self):
    r = ArgumentsExpecationRule()
    self.assertTrue(r.validate())

  def test_validate_with_args(self):
    r = ArgumentsExpecationRule(1,2,2)
    self.assertTrue(r.validate(1,2,2))

    r = ArgumentsExpecationRule(1,1,1)
    self.assertFalse(r.validate(2,2,2))

  def test_validate_with_kwargs(self):
    r = ArgumentsExpecationRule(name="vitaly")
    self.assertTrue(r.validate(name="vitaly"))

    r = ArgumentsExpecationRule(name="vitaly")
    self.assertFalse(r.validate(name="aaron"))

  def test_validate_with_args_and_kwargs(self):
    r = ArgumentsExpecationRule(1, name="vitaly")
    self.assertTrue(r.validate(1, name="vitaly"))

    r = ArgumentsExpecationRule(1, name="vitaly")
    self.assertFalse(r.validate(1, name="aaron"))
  

class ExpecationTest(unittest.TestCase):
  
  def test_default_expecation(self):
    exp = Expectation(object)
    self.assertFalse(exp.closed())
    self.assertTrue(exp.match())
  
  def test_match_with_args(self):
    exp = Expectation(object)
    exp.args(1, 2 ,3)
    
    self.assertTrue(exp.match(1,2,3))
  
  def test_match_with_kwargs(self):
    exp = Expectation(object)
    exp.args(name="vitaly")
    
    self.assertTrue(exp.match(name="vitaly"))

  def test_match_with_both_args_and_kwargs(self):
    exp = Expectation(object)
    exp.args(1, name="vitaly")
    
    self.assertTrue(exp.match(1, name="vitaly"))
  
  def test_closed(self):
    exp = Expectation(object)
    exp.args(1)
    exp.test(1)
    self.assertTrue(exp.closed())

  def test_close(self):
    exp = Expectation(object)
    exp.close()
    self.assertTrue(exp.closed())
  
  def test_return_value_with_value(self):
    exp = Expectation(object)
    exp.returns(123)
    
    self.assertEquals(exp.test(), 123)

  def test_return_value_with_expection_class(self): 
    class CustomException(Exception): pass
    
    exp = Expectation(object)
    exp.raises(CustomException)
    
    self.assertRaises(CustomException, exp.test)

  def test_return_value_with_expection_instance(self): 
    class CustomException(Exception): pass
    
    exp = Expectation(object)
    exp.raises(CustomException())
    
    self.assertRaises(CustomException, exp.test)
  
