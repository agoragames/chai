=================================
 Chai - Python Mocking Made Easy
=================================

:Version: 0.0.1
:Download: http://pypi.python.org/pypi/chai
:Source: https://github.com/agoragames/chai
:Keywords: python, mocking, testing, unittest, unittest2

.. contents::
    :local:

.. _chai-overview:

Overview
========

Chai provides a very easy to use api for mocking/stubbing your python objects, patterned after the `Mocha <http://mocha.rubyforge.org/>` library for Ruby.

.. _chai-example:

Example
=======

The following is an example of a simple test case which is mocking out a get method
on the `CustomObject`. The Chai api allows use of call chains to make the code 
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




.. _chai-features:

Features
========



.. _chai-installation:

Installation
============

You can install Chai either via the Python Package Index (PyPI)
or from source.

To install using `pip`,::

    $ pip install chai

.. _chai-installing-from-source:

Downloading and installing from source
--------------------------------------

Download the latest version of Chai from http://pypi.python.org/pypi/chai

You can install it by doing the following,::

    $ tar xvfz chai-*.*.*.tar.gz
    $ cd celery-*.*.*
    $ python setup.py build
    # python setup.py install # as root

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

