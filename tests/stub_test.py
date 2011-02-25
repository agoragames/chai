
import unittest

from stub import *

class StubTest(unittest.TestCase):

  ###
  ### Test the public stub() method
  ###
  def test_stub_property(self):
    class Foo(object):
      @property
      def prop(self): return 3

    res = stub(Foo, 'prop')
    self.assertTrue( isinstance(res,StubProperty) )
    self.assertEquals( res, stub(Foo,'prop') )
