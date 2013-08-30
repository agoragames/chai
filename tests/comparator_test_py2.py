
import unittest

from chai.comparators import *

class ComparatorsPy2Test(unittest.TestCase):

  # because this code can't be run in py3
  def test_is_a_unicode_test(self):
    comp = IsA(str)
    self.assertTrue( comp.test('foo') )
    self.assertFalse( comp.test(u'foo') )
    self.assertFalse( comp.test(bytearray('foo')) )
