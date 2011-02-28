
import unittest

from chai.comparators import *

class ComparatorsTest(unittest.TestCase):

  def test_equals(self):
    comp = Equals(3)
    self.assertTrue( comp.test(3) )
    self.assertTrue( comp.test(3.0) )
    self.assertFalse( comp.test('3') )

  
