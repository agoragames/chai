
import unittest
from collections import deque

from chai import Chai
from chai.chai import ChaiTestType
from chai.mock import Mock
from chai.stub import Stub
from chai.exception import *
from chai.comparators import Comparator

class CupOf(Chai):
  '''
  An example of a subclass on which we can test certain features.
  '''

  class msg_equals(Comparator):
    '''
    A Comparator used for check message equality
    '''
    #def __init__(self, (key,value)):
    def __init__(self, pair):
      self._key = pair[0]
      self._value = pair[1]

    def test(self, value):
      if isinstance(value,dict):
        return self._value==value.get(self._key)
      return False

  def assert_msg_sent(self, msg):
    '''
    Assert that a message was sent and marked that it was handled.
    '''
    return msg.get('sent_at') and msg.get('received')

  def test_local_definitions_work_and_are_global(self):
    class Foo(object):
      def _save_data(self, msg):
        pass #dosomethingtottalyawesomewiththismessage
        
      def do_it(self, msg):
        self._save_data(msg)
        msg['sent_at'] = 'now'
        msg['received'] = 'yes'

    f = Foo()
    expect( f._save_data ).args( msg_equals(('target','bob')) )
    
    msg = {'target':'bob'}
    f.do_it( msg )
    assert_msg_sent( msg )

  def test_something(self): pass
  def runTest(self, *args, **kwargs): pass

class ChaiTest(unittest.TestCase):

  def test_setup(self):
    case = CupOf()
    case.setup()
    self.assertEquals( deque(), case._stubs )
    self.assertEquals( deque(), case._mocks )

  def test_teardown_closes_out_stubs_and_mocks(self):
      class Stub(object):
        calls = 0
        def teardown(self): self.calls += 1
    
      obj = type('test',(object,),{})()
      setattr(obj, 'mock1', 'foo')
      setattr(obj, 'mock2', 'bar')
      
      case = CupOf()
      stub = Stub()
      case._stubs = deque([stub])
      case._mocks = deque([(obj,'mock1','fee'), (obj,'mock2')])
      case.teardown()
      self.assertEquals( 1, stub.calls )
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
    
  def test_chai_class_use_metaclass(self):
    obj = CupOf()    
    self.assertTrue(obj, ChaiTestType)
    
  def test_runs_unmet_expectations(self):
    class Stub(object):
      unmet_calls = 0
      teardown_calls = 0
      def unmet_expectations(self): self.unmet_calls += 1; return []
      def teardown(self): self.teardown_calls += 1

    # obj = type('test',(object,),{})()
    # setattr(obj, 'mock1', 'foo')
    # setattr(obj, 'mock2', 'bar')
    
    case = CupOf()
    stub = Stub()
    case._stubs = deque([stub])
    
    case.test_local_definitions_work_and_are_global()
    self.assertEquals(1, stub.unmet_calls)
    self.assertEquals(1, stub.teardown_calls)

  def test_raises_if_unmet_expectations(self):
    class Milk(object):
        def pour(self): pass
    milk = Milk()
    case = CupOf()
    stub = Stub(milk.pour)
    stub.expect()
    case._stubs = deque([stub])
    self.assertRaises(ExpectationNotSatisfied, case.test_something)
