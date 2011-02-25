
import unittest

from stub import *

class StubTest(unittest.TestCase):

  def test_stub_property(self):
    class Foo(object):
      @property
      def prop(self): return 3

    
