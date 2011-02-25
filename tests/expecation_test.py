
import unittest
import types

from expectation import *

class ExpecationTest(unittest.TestCase):
  
  def test_default_expecation(self):
    exp = Expectation(object)
    self.assertFalse(exp.closed())
    self.assertTrue(exp.match())
  
  def test_with_args(self):
    exp = Expectation(object)
    exp.args(1, 2 ,3)
    
    self.assertTrue(exp.match(1,2,3))
  
  def test_with_kwargs(self):
    exp = Expectation(object)
    exp.args(name="vitaly")
    
    self.assertTrue(exp.match(name="vitaly"))

  def test_with_both_args_and_kwargs(self):
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
  
