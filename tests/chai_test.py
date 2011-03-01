
import unittest
from collections import deque

from chai import Chai
from chai.mock import Mock
from chai.stub import Stub
from chai.exception import *

class CupOf(Chai):
  def test_something(self): pass
  def runTest(self, *args, **kwargs): pass

class ChaiTest(unittest.TestCase):

  def test_init(self):
    case = CupOf.__new__(CupOf)
    self.assertTrue( hasattr(case, 'assertEquals') )
    self.assertFalse( hasattr(case, 'assert_equals') )
    case.__init__()
    self.assertTrue( hasattr(case, 'assertEquals') )
    self.assertTrue( hasattr(case, 'assert_equals') )

  def test_setup(self):
    case = CupOf()
    case.setup()
    self.assertEquals( deque(), case._stubs )
    self.assertEquals( deque(), case._mocks )

  def test_teardown_closes_out_stubs_and_mocks(self):
    class Stub(object):
      calls = 0
      def assert_expectations(self): self.calls += 1
      def teardown(self): self.calls += 1

    obj = type('test',(object,),{})()
    setattr(obj, 'mock1', 'foo')
    setattr(obj, 'mock2', 'bar')
    
    case = CupOf()
    stub = Stub()
    case._stubs = deque([stub])
    case._mocks = deque([(obj,'mock1','fee'), (obj,'mock2')])
    case.teardown()
    self.assertEquals( 2, stub.calls )
    self.assertEquals( 'fee', obj.mock1 )
    self.assertFalse( hasattr(obj, 'mock2') )

  def test_teardown_closes_out_stubs_and_mocks_when_exception(self):
    class Stub(object):
      calls = 0
      def assert_expectations(self): self.calls += 1; raise ExpectationNotSatisfied('blargh')
      def teardown(self): self.calls += 1

    obj = type('test',(object,),{})()
    setattr(obj, 'mock1', 'foo')
    setattr(obj, 'mock2', 'bar')
    
    case = CupOf()
    stub = Stub()
    case._stubs = deque([stub])
    case._mocks = deque([(obj,'mock1','fee'), (obj,'mock2')])
    self.assertRaises( ExpectationNotSatisfied, case.teardown )
    self.assertEquals( 2, stub.calls )
    self.assertEquals( 'fee', obj.mock1 )
    self.assertFalse( hasattr(obj, 'mock2') )

  def test_stub(self):
    class Milk(object):
      def pour(self): pass

    case = CupOf()
    milk = Milk()
    case.setup()
    self.assertEquals( deque(), case._stubs )
    case.stub( milk.pour )
    self.assertTrue( isinstance(milk.pour, Stub) )
    self.assertEquals( deque([milk.pour]), case._stubs )

    # Test it's only added once
    case.stub( milk, 'pour' )
    self.assertEquals( deque([milk.pour]), case._stubs )

  def test_expect(self):
    class Milk(object):
      def pour(self): pass

    case = CupOf()
    milk = Milk()
    case.setup()
    self.assertEquals( deque(), case._stubs )
    case.expect( milk.pour )
    self.assertEquals( deque([milk.pour]), case._stubs )

    # Test it's only added once
    case.expect( milk, 'pour' )
    self.assertEquals( deque([milk.pour]), case._stubs )

    self.assertEquals( 2, len(milk.pour._expectations) )

  def test_mock_no_binding(self):
    case = CupOf()
    case.setup()

    self.assertEquals( deque(), case._mocks )
    mock1 = case.mock()
    self.assertTrue( isinstance(mock1, Mock) )
    self.assertEquals( deque(), case._mocks )
    mock2 = case.mock()
    self.assertTrue( isinstance(mock2, Mock) )
    self.assertEquals( deque(), case._mocks )
    self.assertNotEqual( mock1, mock2 )

  def test_mock_with_attr_binding(self):
    class Milk(object):
      def __init__(self): self._case = []
      def pour(self): return self._case.pop(0)

    case = CupOf()
    case.setup()
    milk = Milk()
    orig_pour = milk.pour

    self.assertEquals( deque(), case._mocks )
    mock1 = case.mock( milk, 'pour' )
    self.assertTrue( isinstance(mock1, Mock) )
    self.assertEquals( deque([(milk,'pour',orig_pour)]), case._mocks )
    mock2 = case.mock( milk, 'pour' )
    self.assertTrue( isinstance(mock2, Mock) )
    self.assertEquals( deque([(milk,'pour',orig_pour),(milk,'pour',mock1)]), case._mocks )
    self.assertNotEqual( mock1, mock2 )

    mock3 = case.mock( milk, 'foo' )
    self.assertTrue( isinstance(mock3, Mock) )
    self.assertEquals( deque([(milk,'pour',orig_pour),(milk,'pour',mock1),(milk,'foo')]), case._mocks )
