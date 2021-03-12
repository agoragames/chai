import unittest
import sys

from chai.stub import *
from chai.mock import Mock
import tests.samples as samples

try:
    IS_PYPY = sys.subversion[0] == 'PyPy'
except AttributeError:
    IS_PYPY = False


class StubTest(unittest.TestCase):
  """
  Test the public stub() method
  """
  def test_stub_property_on_class_with_attr_name(self):
    class Foo(object):
      @property
      def prop(self): return 3

    res = stub(Foo, 'prop')
    self.assertTrue(isinstance(res,StubProperty))
    self.assertTrue(stub(Foo,'prop') is res)

  def test_stub_property_on_instance_with_attr_name(self):
    class Foo(object):
      @property
      def prop(self): return 3
    foo = Foo()

    res = stub(foo, 'prop')
    self.assertTrue(isinstance(res,StubProperty))
    self.assertTrue(stub(foo,'prop') is res)

  def test_stub_property_on_class_with_attr_name_applies_to_instance(self):
    class Foo(object):
      @property
      def prop(self): return 3

    foo = Foo()
    res = stub(Foo, 'prop')
    self.assertTrue(stub(foo,'prop') is res)

  def test_stub_property_with_obj_ref_for_the_reader(self):
    class Foo(object):
      @property
      def prop(self): return 3

    res = stub(Foo.prop)
    self.assertTrue(isinstance(res, StubProperty))
    self.assertTrue(stub(Foo.prop) is res)

  @unittest.skipIf(IS_PYPY, "can't stub property setter in PyPy")
  def test_stub_property_with_obj_ref_for_the_setter(self):
    class Foo(object):
      @property
      def prop(self): return 3

    res = stub(Foo.prop.setter)
    self.assertTrue(isinstance(res, StubMethod))
    self.assertTrue(isinstance(Foo.prop, StubProperty))

  @unittest.skipIf(IS_PYPY, "can't stub property deleter in PyPy")
  def test_stub_property_with_obj_ref_for_the_deleter(self):
    class Foo(object):
      @property
      def prop(self): return 3

    res = stub(Foo.prop.deleter)
    self.assertTrue(isinstance(res, StubMethod))
    self.assertTrue(isinstance(Foo.prop, StubProperty))

  def test_stub_mock_with_attr_name(self):
    class Foo(object):
      def bar(self): pass

    f = Foo()
    f.bar = Mock()
    res = stub(f, 'bar')
    self.assertTrue(isinstance(res, StubMethod))
    self.assertEqual(res, f.bar.__call__)
    self.assertEqual(res, stub(f, 'bar'))

  def test_stub_mock_with_obj_ref(self):
    class Foo(object):
      def bar(self): pass

    f = Foo()
    f.bar = Mock()
    res = stub(f.bar)
    self.assertTrue(isinstance(res, StubMethod))
    self.assertEqual(res, f.bar.__call__)
    self.assertEqual(res, stub(f.bar))

  def test_stub_type_with_obj_ref(self):
    class Foo(object):
      def bar(self): pass

    res = stub(Foo)
    self.assertTrue(isinstance(res, StubNew))
    self.assertEqual(res, Foo.__new__)
    self.assertEqual(res, stub(Foo))

    # test that __init__ called only once
    res.expect()
    self.assertEqual(1, len(res._expectations))
    res = stub(Foo)
    self.assertEqual(1, len(res._expectations))

  def test_stub_unbound_method_with_attr_name(self):
    class Foo(object):
      def bar(self): pass

    res = stub(Foo, 'bar')
    self.assertTrue(isinstance(res,StubUnboundMethod))
    self.assertEqual(res, stub(Foo,'bar'))
    self.assertEqual(res, getattr(Foo,'bar'))

  @unittest.skipIf(sys.version_info.major==3, "can't stub unbound methods by reference in python 3")
  def test_stub_unbound_method_with_obj_ref(self):
    class Foo(object):
      def bar(self): pass

    res = stub(Foo.bar)
    self.assertTrue(isinstance(res,StubUnboundMethod))
    self.assertEqual(res, stub(Foo.bar))
    self.assertEqual(res, getattr(Foo,'bar'))

  def test_stub_bound_method_for_instance_with_attr_name(self):
    class Foo(object):
      def bar(self): pass

    foo = Foo()
    orig = foo.bar
    res = stub(foo, 'bar')
    self.assertTrue(isinstance(res,StubMethod))
    self.assertEqual(res._instance, foo)
    self.assertEqual(res._obj, orig)
    self.assertEqual(res._attr, 'bar')
    self.assertEqual(res, stub(foo,'bar'))
    self.assertEqual(res, getattr(foo,'bar'))

  def test_stub_bound_method_for_instance_with_obj_ref(self):
    class Foo(object):
      def bar(self): pass

    foo = Foo()
    orig = foo.bar
    res = stub(foo.bar)
    self.assertTrue(isinstance(res,StubMethod))
    self.assertEqual(res._instance, foo)
    self.assertEqual(res._obj, orig)
    self.assertEqual(res._attr, 'bar')
    self.assertEqual(res, stub(foo.bar))
    self.assertEqual(res, getattr(foo,'bar'))

  def test_stub_bound_method_for_classmethod_with_attr_name(self):
    class Foo(object):
      @classmethod
      def bar(self): pass

    res = stub(Foo, 'bar')
    self.assertTrue(isinstance(res,StubMethod))
    self.assertEqual(res, stub(Foo,'bar'))
    self.assertEqual(res, getattr(Foo,'bar'))

  def test_stub_bound_method_for_classmethod_with_obj_ref(self):
    class Foo(object):
      @classmethod
      def bar(self): pass

    res = stub(Foo.bar)
    self.assertTrue(isinstance(res,StubMethod))
    self.assertEqual(res, stub(Foo.bar))
    self.assertEqual(res, getattr(Foo,'bar'))

  @unittest.skipIf(IS_PYPY, "no method-wrapper in PyPy")
  def test_stub_method_wrapper_with_attr_name(self):
    class Foo(object): pass

    foo = Foo()
    res = stub(foo, '__hash__')
    self.assertTrue(isinstance(res,StubMethodWrapper))
    self.assertEqual(res, stub(foo, '__hash__'))
    self.assertEqual(res, getattr(foo, '__hash__'))

  @unittest.skipIf(IS_PYPY, "no method-wrapper in PyPy")
  def test_stub_method_wrapper_with_obj_ref(self):
    class Foo(object): pass

    foo = Foo()
    res = stub(foo.__hash__)
    self.assertTrue(isinstance(res,StubMethodWrapper))
    self.assertEqual(res, stub(foo.__hash__))
    self.assertEqual(res, getattr(foo, '__hash__'))

  def test_stub_module_function_with_attr_name(self):
    res = stub(samples, 'mod_func_1')
    self.assertTrue(isinstance(res,StubFunction))
    self.assertEqual(res, getattr(samples,'mod_func_1'))
    self.assertEqual(res, stub(samples,'mod_func_1'))
    res.teardown()

  def test_stub_module_function_with_obj_ref(self):
    res = stub(samples.mod_func_1)
    self.assertTrue(isinstance(res,StubFunction))
    self.assertEqual(res, getattr(samples,'mod_func_1'))
    self.assertEqual(res, samples.mod_func_1)
    self.assertEqual(res, stub(samples.mod_func_1))
    res.teardown()

class StubClassTest(unittest.TestCase):
  ###
  ### Test Stub class (if only I could mock my mocking mocks)
  ###
  def test_init(self):
    s = Stub('obj','attr')
    self.assertEqual('obj', s._obj)
    self.assertEqual('attr', s._attr)
    self.assertEqual([], s._expectations)

  def test_unment_expectations(self):
    s = Stub('obj', 'attr')
    s.expect().args(123).returns(1)

    self.assertTrue(all([isinstance(e, ExpectationNotSatisfied) for e in s.unmet_expectations()]))

  def test_teardown(self):
    s = Stub('obj')
    s._expections = ['1','2']
    s.teardown()
    self.assertEqual([], s._expectations)

  def test_expect(self):
    s = Stub('obj')

    self.assertEqual([], s._expectations)
    e = s.expect()
    self.assertEqual([e], s._expectations)
    self.assertEqual(s, e._stub)

  def test_call_orig_raises_notimplemented(self):
    s = Stub('obj')

    with self.assertRaises(NotImplementedError):
      s.call_orig(1,2,a='b')

  def test_call_raises_unexpected_call_when_no_expectations(self):
    s = Stub('obj')
    self.assertRaises(UnexpectedCall, s, 'foo')

  def test_call_when_args_match(self):
    class Expect(object):
      def closed(self): return False
      def match(self, *args, **kwargs): return True
      def test(self, *args, **kwargs): return 'success'

    s = Stub('obj')
    s._expectations = [ Expect() ]
    self.assertEqual('success', s('foo'))

  def test_call_raises_unexpected_call_when_all_expectations_closed(self):
    class Expect(object):
      def closed(self): return True

    s = Stub('obj')
    s._expectations = [ Expect(), Expect() ]
    self.assertRaises(UnexpectedCall, s, 'foo')

  def test_call_raises_unexpected_call_when_closed_and_no_matching(self):
    class Expect(object):
      def __init__(self, closed):
        self._closed=closed
        self._match_count = 0
        self._close_count=0
      def closed(self):
        return self._closed
      def match(self, *args, **kwargs):
        self._match_count +=1
        return False
      def close(self, *args, **kwargs):
        self._close_count += 1
        self._close_args = (args,kwargs)
      def counts_met(self):
        return self._closed
      def is_any_order(self):
        return False

    s = Stub('obj')
    s._expectations = [ Expect(True), Expect(False) ]
    self.assertRaises(UnexpectedCall, s, 'foo')
    self.assertEqual(0, s._expectations[0]._match_count)
    self.assertEqual(1, s._expectations[1]._match_count)
    self.assertEqual(0, s._expectations[0]._close_count)
    self.assertEqual(0, s._expectations[1]._close_count)

class StubPropertyTest(unittest.TestCase):
  # FIXME: Need to test teardown and init, these test might be in the base stub tests.

  def test_name(self):
    class Foo(object):
      @property
      def prop(self): return 3

    s = StubProperty(Foo, 'prop')
    self.assertEqual(s.name, 'Foo.prop')

class StubMethodTest(unittest.TestCase):

  def test_init(self):
    class Foo(object):
      def bar(self): pass

    f = Foo()
    orig = f.bar
    s = StubMethod(f.bar)
    self.assertEqual(s._obj, orig)
    self.assertEqual(s._instance, f)
    self.assertEqual(s._attr, 'bar')
    self.assertEqual(s, getattr(f,'bar'))

    f = Foo()
    orig = f.bar
    s = StubMethod(f, 'bar')
    self.assertEqual(s._obj, orig)
    self.assertEqual(s._instance, f)
    self.assertEqual(s._attr, 'bar')
    self.assertEqual(s, getattr(f,'bar'))

  def test_name(self):
    class Expect(object):
      def closed(self): return False
    obj = Expect()
    s = StubMethod(obj.closed)
    self.assertEqual("Expect.closed", s.name)
    s.teardown()

    s = StubMethod(obj, 'closed')
    self.assertEqual("Expect.closed", s.name)
    s.teardown()

  def test_call_orig(self):
    class Foo(object):
      def __init__(self, val): self._val = val
      def a(self): return self._val
      def b(self, val): self._val = val

    f = Foo(3)
    sa = StubMethod(f.a)
    sb = StubMethod(f.b)
    self.assertEqual(3, sa.call_orig())
    sb.call_orig(5)
    self.assertEqual(5, sa.call_orig())

  def test_teardown(self):
    class Foo(object):
      def bar(self): pass

    f = Foo()
    orig = f.bar
    s = StubMethod(f.bar)
    s.teardown()
    self.assertEqual(orig, f.bar)

  def test_teardown_of_classmethods(self):
    class Foo(object):
      @classmethod
      def bar(self): pass

    self.assertTrue(isinstance(Foo.__dict__['bar'], classmethod))
    s = StubMethod(Foo.bar)
    s.teardown()
    self.assertTrue(isinstance(Foo.__dict__['bar'], classmethod), "Is not a classmethod")

  def test_teardown_of_bound_instance_methods_exported_in_module(self):
    orig = samples.mod_instance_foo
    s = StubMethod(samples, 'mod_instance_foo')
    s.teardown()
    self.assertEqual(orig, samples.mod_instance_foo)

class StubFunctionTest(unittest.TestCase):

  def test_init(self):
    s = StubFunction(samples.mod_func_1)
    self.assertEqual(s._instance, samples)
    self.assertEqual(s._attr, 'mod_func_1')
    self.assertEqual(s, samples.mod_func_1)
    self.assertEqual(False, s._was_object_method)
    s.teardown()

  def test_init_with_object_method(self):
    x = samples.SampleBase()
    s = StubFunction(x, '__new__')
    self.assertEqual(True, s._was_object_method)

  def test_name(self):
    s = StubFunction(samples.mod_func_1)
    self.assertEqual('tests.samples.mod_func_1', s.name)
    s.teardown()

  def test_call_orig(self):
    s = StubFunction(samples.mod_func_3)
    self.assertEqual(12, s.call_orig(4))
    s.teardown()

  def test_teardown(self):
    orig = samples.mod_func_1
    s = StubFunction(samples.mod_func_1)
    s.teardown()
    self.assertEqual(orig, samples.mod_func_1)

  def test_teardown_on_object_method(self):
    x = samples.SampleBase()
    self.assertEqual(object.__new__, getattr(x, '__new__'))
    s = StubFunction(x, '__new__')
    self.assertNotEqual(object.__new__, getattr(x, '__new__'))
    s.teardown()
    self.assertEqual(object.__new__, getattr(x, '__new__'))

class StubNewTest(unittest.TestCase):

  @unittest.skipIf(sys.version_info.major==3, "can't stub unbound methods in python 3")
  def test_new(self):
    class Foo(object): pass

    self.assertEqual(0, len(StubNew._cache))
    x = StubNew(Foo)
    self.assertTrue(x is StubNew(Foo))
    self.assertEqual(1, len(StubNew._cache))
    StubNew._cache.clear()

  def test_init(self):
    class Foo(object): pass

    s = StubNew(Foo)
    self.assertEqual(s._instance, Foo)
    self.assertEqual(s._attr, '__new__')
    self.assertEqual(s, Foo.__new__)
    s.teardown()

  def test_call(self):
    class Foo(object): pass
    class Expect(object):
      def closed(self): return False
      def match(self, *args, **kwargs): return args==('state',) and kwargs=={'a':'b'}
      def test(self, *args, **kwargs): return 'success'

    s = StubNew(Foo)
    s._expectations = [ Expect() ]
    self.assertEqual('success', Foo('state', a='b'))
    s.teardown()

  @unittest.skipIf(sys.version_info.major==3, "can't stub unbound methods in python 3")
  def test_call_orig(self):
    class Foo(object):
      def __init__(self, val):
        self._val = val

    StubNew._cache.clear()
    s = StubNew(Foo)
    f = s.call_orig(3)
    self.assertTrue(isinstance(f,Foo))
    self.assertEqual(3, f._val)
    s.teardown()
    StubNew._cache.clear()

  @unittest.skipIf(sys.version_info.major==3, "can't stub unbound methods in python 3")
  def test_teardown(self):
    class Foo(object): pass

    orig = Foo.__new__
    self.assertEqual(0, len(StubNew._cache))
    x = StubNew(Foo)
    self.assertEqual(1, len(StubNew._cache))
    x.teardown()
    self.assertEqual(0, len(StubNew._cache))
    self.assertEqual(orig, Foo.__new__)

  @unittest.skipIf(sys.version_info.major==3, "can't stub unbound methods in python 3")
  def test_teardown_on_custom_new(self):
    class Foo(object):
      def __new__(cls, *args, **kwargs):
        rval = object.__new__(cls)
        rval.args = args
        return rval

    f1 = Foo('f1')
    self.assertEqual(('f1',), f1.args)
    orig = Foo.__new__
    self.assertEqual(0, len(StubNew._cache))
    x = StubNew(Foo)
    self.assertEqual(1, len(StubNew._cache))
    x.teardown()
    self.assertEqual(0, len(StubNew._cache))
    self.assertEqual(orig, Foo.__new__)
    f2 = Foo('f2')
    self.assertEqual(('f2',), f2.args)


class StubUnboundMethodTest(unittest.TestCase):

  def test_init(self):
    class Foo(object):
      def bar(self): pass

    s = StubUnboundMethod(Foo, 'bar')
    self.assertEqual(s._instance, Foo)
    self.assertEqual(s._attr, 'bar')
    self.assertEqual(s, getattr(Foo,'bar'))

  def test_name(self):
    class Expect(object):
      def closed(self): return False

    s = StubUnboundMethod(Expect, 'closed')
    self.assertEqual("Expect.closed", s.name)
    s.teardown()

  def test_teardown(self):
    class Foo(object):
      def bar(self): pass

    orig = Foo.bar
    s = StubUnboundMethod(Foo, 'bar')
    s.teardown()
    self.assertEqual(orig, Foo.bar)

  def test_call_acts_as_any_instance(self):
    class Foo(object):
      def bar(self): pass

    class StubIntercept(StubUnboundMethod):
      calls = 0
      def __call__(self, *args, **kwargs):
        self.calls += 1

    orig = Foo.bar
    s = StubIntercept(Foo, 'bar')

    f1 = Foo()
    f1.bar()
    f2 = Foo()
    f2.bar()

    self.assertEqual(2, s.calls)

class StubMethodWrapperTest(unittest.TestCase):

  def test_init(self):
    class Foo(object):pass
    foo = Foo()

    s = StubMethodWrapper(foo.__hash__)
    self.assertEqual(s._instance, foo)
    self.assertEqual(s._attr, '__hash__')
    self.assertEqual(s, getattr(foo,'__hash__'))

  def test_name(self):
    class Foo(object):pass
    foo = Foo()

    s = StubMethodWrapper(foo.__hash__)
    self.assertEqual("Foo.__hash__", s.name)
    s.teardown()

  def test_call_orig(self):
    class Foo(object):
      def __init__(self, val): self._val = val
      def get(self): return self._val
      def set(self, val): self._val = val

    f = Foo(3)
    sg = StubMethodWrapper(f.get)
    ss = StubMethodWrapper(f.set)

    self.assertEqual(3, sg.call_orig())
    ss.call_orig(5)
    self.assertEqual(5, sg.call_orig())

  def test_teardown(self):
    class Foo(object):pass
    obj = Foo()
    orig = obj.__hash__
    s = StubMethodWrapper(obj.__hash__)
    s.teardown()
    self.assertEqual(orig, obj.__hash__)

@unittest.skipIf(IS_PYPY, "no method-wrapper in PyPy")
class StubWrapperDescriptionTest(unittest.TestCase):

  def test_init(self):
    class Foo(object):pass
    s = StubWrapperDescriptor(Foo, '__hash__')
    self.assertEqual(s._obj, Foo)
    self.assertEqual(s._attr, '__hash__')
    self.assertEqual(s, getattr(Foo,'__hash__'))

  def test_name(self):
    class Foo(object):pass

    s = StubWrapperDescriptor(Foo, '__hash__')
    self.assertEqual("Foo.__hash__", s.name)
    s.teardown()

  def test_call_orig(self):
    class Foo(object): pass
    if sys.version_info < (3, 3):
      foo_str = "<class 'test_stub.Foo'>"
    else:
      foo_str = "<class 'test_stub.StubWrapperDescriptionTest.test_call_orig.<locals>.Foo'>"

    s = StubWrapperDescriptor(Foo, '__str__')
    self.assertEqual(foo_str, s.call_orig())
    s.teardown()

  def test_teardown(self):
    class Foo(object):pass
    orig = Foo.__hash__
    s = StubWrapperDescriptor(Foo, '__hash__')
    s.teardown()
    self.assertEqual(orig, Foo.__hash__)
