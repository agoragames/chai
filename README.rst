=================================
 Chai - Python Mocking Made Easy
=================================

:Version: 0.1.21
:Download: http://pypi.python.org/pypi/chai
:Source: https://github.com/agoragames/chai
:Keywords: python, mocking, testing, unittest, unittest2

.. contents::
    :local:

.. _chai-overview:

Overview
========

Chai provides a very easy to use api for mocking/stubbing your python objects, patterned after the `Mocha <http://mocha.rubyforge.org/>`_ library for Ruby.

.. _chai-example:

Example
=======

The following is an example of a simple test case which is mocking out a get method
on the ``CustomObject``. The Chai api allows use of call chains to make the code 
short, clean, and very readable. It also does away with the standard setup-and-replay
work flow, giving you more flexibility in how you write your cases. ::


    from chai import Chai

    class CustomObject (object): 
        def get(self, arg):
            pass

    class TestCase(Chai):
        def test_mock_get(self):
            obj = CustomObject()
            self.expect(obj.get).args('name').returns('My Name')
            self.assert_equals(obj.get('name'), 'My Name')
            self.expect(obj.get).args('name').returns('Your Name')
            self.assert_equals(obj.get('name'), 'Your Name')

        def test_mock_get_with_at_most(self):
            obj = CustomObject()
            self.expect(obj.get).args('name').returns('My Name').at_most(2)
            self.assert_equals(obj.get('name'), 'My Name')
            self.assert_equals(obj.get('name'), 'My Name')
            self.assert_equals(obj.get('name'), 'My Name') # this one will fail

    if __name__ == '__main__':
        import unittest2
        unittest2.main()


.. _chai-api:

API
===

All of the features are available by extending the ``Chai`` class, itself a subclass of ``unittest.TestCase``. If ``unittest2`` is available Chai will use that, else it will fall back to ``unittest``. Chai also aliases all of the ``assert*`` methods to lower-case with undersores. For example, ``assertNotEquals`` can also be referenced as ``assert_not_equals``.

Additionally, ``Chai`` loads in all assertions, comparators and mocking methods into the module in which a ``Chai`` subclass is declared. This is done to cut down on the verbosity of typing ``self.`` everywhere that you want to run a test.  The references are loaded into the subclass' module during ``setUp``, so you're sure any method you call will be a reference to the class and module in which a particular test method is currently being executed. Methods and comparators you define locally in a test case will be globally available when you're running that particular case as well. ::
    
    class ProtocolInterface(object): 
        def _private_call(self, arg):
            pass
        def get_result(self, arg): 
            self._private_call(arg)
            return 'ok'
    
    class TestCase(Chai):
        def assert_complicated_state(self, obj):
            return True  # ..or.. raise AssertionError()

        def test_mock_get(self):
            obj = ProtocolInterface()
            data = object()
            expect(obj._private_call).args(data)
            assert_equals('ok', obj.get_result(data))
            assert_complicated_state(data)

Stubbing
--------

The simplest mock is to stub a method. This replaces the original method with a subclass of ``chai.Stub``, the main instrumentation class. All additional ``stub`` and ``expect`` calls will re-use this stub, and the stub is responsible for re-installing the original reference when ``Chai.tearDown`` is run.

Stubbing is used for situations when you want to assert that a method is never called. ::

    class CustomObject (object): 
        def get(self, arg):
            pass
        @property
        def prop(self):
            pass

    class TestCase(Chai):
        def test_mock_get(self):
            obj = CustomObject()
            stub(obj.get)
            assert_raises( UnexpectedCall, obj.get )

In this example, we can reference ``obj.get`` directly because ``get`` is a bound method and provides all of the context we need to refer back to ``obj`` and stub the method accordingly. There are cases where this is insufficient, such as module imports, special Python types, and when module attributes are imported from another (like ``os`` and ``posix``). If the object can't be stubbed with a reference, ``UnsupportedStub`` will be raised and you can use the verbose reference instead. ::
    
    class TestCase(Chai):
        def test_mock_get(self):
            obj = CustomObject()
            stub(obj, 'get')
            assert_raises( UnexpectedCall, obj.get )

Stubbing an unbound method will apply that stub to all future instances of that class. ::
    
    class TestCase(Chai):
        def test_mock_get(self):
            stub(CustomObject.get)
            obj = CustomObject()
            assert_raises( UnexpectedCall, obj.get )

Some methods cannot be stubbed because it is impossible to call ``setattr`` on the object. A good example of this is the ``datetime.datetime`` class.

Finally, Chai supports stubbing of properties on classes. In all cases, the stub will be applied to a class and individually to each of the 3 property methods. Because the stub is on the class, all instances need to be addressed when you write expectations. The first interface is via the named attribute method which can be used on both classes and instances. ::

    class TestCase(Chai):
        def test_prop_attr(self):
            obj = CustomObject()
            stub( obj, 'prop' )
            assert_raises( UnexpectedCall, lambda: obj.prop )
            stub( stub( obj, 'prop' ).setter )

Using the class, you can directly refer to all 3 methods of the property. To refer to the getter you use the property directly, and for the methods you use its associated attribute name. You can stub in any order and it will still resolve correctly. ::

    class TestCase(Chai):
      def test_prop_attr(self):
        stub( CustomObject.prop.setter )
        stub( CustomObject.prop )
        stub( CustomObject.prop.deleter )
        assert_raises( UnexpectedCall, lambda: CustomObject().prop )


Expectation
-----------

Expectations are individual test cases that can be applied to a stub. They are expected to be run in order (unless otherwise noted). They are greedy, in that so long as an expectation has not been met and the arguments match, the arguments will be processed by that expectation. This mostly applies to the "at_least" and "any_order" expectations, which (may) stay open throughout the test and will handle any matching call.

Expectations will automatically create a stub if it's not already applied, so no separate call to ``stub`` is necessary. The arguments and edge cases regarding what can and cannot have expectations applied are identical to stubs. The ``expect`` call will return a new ``chai.Expectation`` object which can then be used to modify the expectation. Without any modifiers, an expectation will expect a single call without arguments and return None. ::

    class TestCase(Chai):
        def test_mock_get(self):
            obj = CustomObject()
            expect(obj.get)
            assert_equals( None, obj.get() )
            assert_raises( UnexpectedCall, obj.get )

Modifiers can be applied to the expectation. Each modifier will return a reference to the expectation for easy chaining. In this example, we're going to match a parameter and change the behavior depending on the argument. This also shows the ability to incrementally add expectations throughout the test. ::

    class TestCase(Chai):
        def test_mock_get(self):
            obj = CustomObject()
            expect(obj.get).args('foo').returns('hello').times(2)
            assert_equals( 'hello', obj.get('foo') )
            assert_equals( 'hello', obj.get('foo') )
            expect(obj.get).args('bar').raises( ValueError )
            assert_raises( ValueError, obj.get, 'bar' )

It is very common to need to run expectations on the constructor for an object, possibly including returning a mock object. Chai makes this very simple. ::

    def method():
        obj = CustomObject('state')
        obj.save()
        return obj

    class TestCase(Chai):
        def test_method(self):
            obj = mock()
            expect( CustomObject ).args('state').returns( obj )
            expect( obj.save )
            assert_equals( obj, method() )
    

Lastly, the arguments modifier supports several matching functions. For simplicity in covering the common cases, the arg expectation assumes an equals test for instances and an instanceof test for types. All rules that apply to positional arguments also apply to keyword arguments. ::

    class TestCase(Chai):
        def test_mock_get(self):
            obj = CustomObject()
            expect(obj.get).args(is_a(float)).returns(42)
            assert_raises( UnexpectedCall, obj.get, 3 )
            assert_equals( 42, obj.get(3.14) )
            
            expect(obj.get).args(str).returns('yes')
            assert_equals( 'yes', obj.get('no') )

            expect(obj.get).args(is_arg(list)).return('yes')
            assert_raises( UnexpectedCall, obj.get, [] )
            assert_equals( 'yes', obj.get(list) )

Modifiers
+++++++++

Expectations expose the following public methods for changing their behavior.


args(``*args``, ``**kwargs``)
  Add a test to the expectation for matching arguments.

any_args
  Any arguments are accepted.

returns(object)
  Add a return value to the expectation when it is matched and executed.

raises(exception)
  When the expectation is run it will raise this exception. Accepts type or instance.

times(int)
  An integer that defines a hard limit on the minimum and maximum number of times the expectation should be executed.

at_least(int)
  Sets a minimum number of times the expectation should run and removes any maximum.

at_least_once
  Equivalent to ``at_least(1)``.

at_most(int)
  Sets a maximum number of times the expectation should run. Does not affect the minimum.

at_most_once
  Equivalent to ``at_most(1)``.

once
  Equivalent to ``times(1)``, also the default for any expectation.

any_order
  The expectation can be called at any time, independent of when it was defined. Can be combined with ``at_least_once`` to force it to respond to all matching calls throughout the test.

side_effect(callable)
  Called with a function argument. When the expectation passes a test, the function will be executed. The side effect will be executed even if the expectation is configured to raise an exception.

teardown
  Will remove the stub after the expectation has been met. This is useful in cases where you need to mock core methods such as ``open``, but immediately return its original behavior after the mocked call has run.
  

Argument Comparators
++++++++++++++++++++

Argument comparators are defined as classes in ``chai.comparators``, but loaded into the ``Chai`` class for convenience (and by extension, a subclass' module).

equals(object)
  The default comparator, uses standard Python equals operator

almost_equals(float, places)
  Identical to assertAlmostEquals, will match an argument to the comparator value to a most ``places`` digits beyond the decimal point.

is_a(type)
  Match an argument of a given type. Supports same arguments as builtin function ``isinstance``.

is_arg(object)
  Matches an argument using the Python ``is`` comparator.

any_of(comparator_list)
  Matches an argument if any of the comparators in the argument list are met. Uses automatic comparator generation for instances and types in the list.

all_of(comparator_list)
  Matches an argument if all of the comparators in the argument list are met. Uses automatic comparator generation for instances and types in the list.

not_of(comparator)
  Matches an argument if the supplied comparator does not match.

matches(pattern)
  Matches an argument using a regular expression. Standard ``re`` rules apply.

func(callable)
  Matches an argument if the callable returns True. The callable must take one argument, the parameter being checked.

ignore
  Matches any argument.

in_arg(in_list)
  Matches if the argument is in the ``in_list``.

contains(object)
  Matches if the argument contains the object using the Python ``in`` function.

like(container)
  Matches if the argument contains all of the same items as in ``container``. Insists that the argument is the same type as ``container``. Useful when you need to assert a few values in a list or dictionary, but the exact contents are not known or can vary.

var(name)
  A variable match against the first time that the argument is called. In the case of multiple calls, the second one must match the previous value of ``name``. After your tests have run, you can check the value against expected arguments through ``var(name).value``. This is really useful when you're testing a deep stack and it's simpler to assert that "value A was used in method call X".


**A note of caution**
If you are using the ``func`` comparator to produce side effects, be aware that it may be called more than once even if the expectation you're defining only occurs once. This is due to the way ``Stub.__call__`` processes the expectations and determines when to process arguments through an expectation.


Context Manager
+++++++++++++++

An expectation can act as a context manager, which is very useful in complex mocking situations. The context will always be the return value for the expectation. For example: ::

  def get_cursor(cname):
      return db.Connection( 'host:port' ).collection( cname ).cursor()

  def test_get_cursor():
      with expect( db.Connection ).any_args().returns( mock() ) as connection:
          with expect( connection.collection ).args( 'collection' ).returns( mock() ) as collection:
              expect( collection.cursor ).returns( 'cursor' )

      assert_equals( 'cursor', get_cursor('collection') )

Mock
----

Sometimes you need a mock object which can be used to stub and expect anything. Chai exposes this through the ``mock`` method which can be called in one of two ways.

Without any arguments, ``Chai.mock()`` will return a ``chai.Mock`` object that can be used for any purpose. If called with arguments, it behaves like ``stub`` and ``expect``, creating a Mock object and setting it as the attribute on another object.

Any request for an attribute from a Mock will return a new Mock object, but ``setattr`` behaves as expected so it can store state as well. The dynamic function will act like a stub, raising ``UnexpectedCall`` if no expectation is defined. ::

    class CustomObject(object):
        def __init__(self, handle):
            _handle = handle
        def do(self, arg):
            return _handle.do(arg)

    class TestCase(Chai):
        def test_mock_get(self):
            obj = CustomObject( mock() )
            expect( obj._handle.do ).args('it').returns('ok')
            assert_equals('ok', obj.do('it'))
            assert_raises( UnexpectedCall, obj._handle.do_it_again )

The ``stub`` and ``expect`` methods handle ``Mock`` objects as arguments by mocking the ``__call__`` method, which can also act in place of ``__init__``. ::

    # module custom.py
    from collections import deque

    class CustomObject(object):
        def __init__(self):
            self._stack = deque()

    # module custom_test.py
    import custom
    from custom import CustomObject

    class TestCase(Chai):
        def test_mock_get(self):
            mock( custom, 'deque' )
            expect( custom.deque ).returns( 'stack' )

            obj = CustomObject()
            assert_equals('stack', obj._stack)

``Mock`` objects, because of the ``getattr`` implementation, can also support nested attributes. ::

    class TestCase(Chai):
        def test_mock(self):
          m = mock()
          m.id = 42
          expect( m.foo.bar ).returns( 'hello' )
          assert_equals( 'hello', m.foo.bar() )
          assert_equals( 42, m.id )

In addition to implementing ``__call__``, ``Mock`` objects implement ``__nonzero__``, 
the container and context manager interfaces are defined. Nonzero will always return
``True``; other methods will raise ``UnexpectedCall``.  The ``__getattr__`` method
cannot be itself stubbed.

.. _chai-installation:

Installation
============

You can install Chai either via the Python Package Index (PyPI)
or from source.

To install using ``pip``,::

    $ pip install chai

.. _chai-installing-from-source:

Downloading and installing from source
--------------------------------------

Download the latest version of Chai from http://pypi.python.org/pypi/chai

You can install it by doing the following,::

    $ tar xvfz chai-*.*.*.tar.gz
    $ cd chai-*.*.*.tar.gz
    $ python setup.py install # as root

.. _chai-installing-from-git:

Using the development version
-----------------------------

You can clone the repository by doing the following::

    $ git clone git://github.com/agoragames/chai.git

.. _bug-tracker:

Bug tracker
===========

If you have any suggestions, bug reports or annoyances please report them
to our issue tracker at https://github.com/agoragames/chai/issues

.. _license:

License
=======

This software is licensed under the `New BSD License`. See the ``LICENSE``
file in the top distribution directory for the full license text.

.. # vim: syntax=rst expandtab tabstop=4 shiftwidth=4 shiftround

