mock is a Python module that provides a core Mock class. It is intended to
reduce the need for creating a host of trivial stubs throughout your test suite.
After performing an action, you can make assertions about which methods /
attributes were used and arguments they were called with. You can also specify 
return values and set needed attributes in the normal way.

This approach is inspired by the testing patterns used at
`Resolver Systems <http://www.resolversystems.com/>`_.

mock is tested on Python versions 2.4 - 2.7.

The mock module also provides utility functions / objects to assist with
testing, particularly monkey patching.

Mock is very easy to use and is designed for use with
`unittest <http://pypi.python.org/pypi/unittest2 unittest>`_. Mock is based on
the 'action -> assertion' pattern instead of 'record -> replay' used by many
mocking frameworks. See the 
`mock documentation <http://www.voidspace.org.uk/python/mock/>`_ for full
details.

Mock objects create all attributes and methods as you access them and store
details of how they have been used. You can configure them, to specify return
values or limit what attributes are available, and then make assertions about
how they have been used::

    >>> from mock import Mock
    >>> real = ProductionClass()
    >>> real.method = Mock()
    >>> real.method.return_value = 3
    >>>
    >>> real.method(3, 4, 5, key='value')
    3
    >>> real.method.assert_called_with(3, 4, 5, key='value')

The ``patch`` decorator / context manager makes it easy to mock classes or
objects in a module under test. The object you specify will be replaced with a
mock (or other object) during the test and restored when the test ends::
    
    @patch('test_module.ClassName1')
    @patch('test_module.ClassName2')
    def test_method(self, MockClass1, MockClass2):
        test_module.ClassName1()
        test_module.ClassName2()
    
        self.assertTrue(MockClass1.called, "ClassName1 not patched")
        self.assertTrue(MockClass2.called, "ClassName2 not patched")


The version of mock.py in `SVN <http://code.google.com/p/mock/source/browse/>`_,
which will be released as version 0.7, supports the mocking of magic methods and
also works with Python 3. The easiest way of using magic methods is with the
``MagicMock`` class. It allows you to do things like::

    >>> from mock import MagicMock
    >>> mock = MagicMock()
    >>> mock.__str__.return_value = 'foobarbaz'
    >>> str(mock)
    'foobarbaz'
    >>> mock.__str__.assert_called_with()

In 0.7 Mock allows you to assign functions (or other Mock instances) to magic
methods and they will be called appropriately. The MagicMock class is just a
Mock variant that has all of the magic methods pre-created for you (well - all
the useful ones anyway).

The following is an example of using magic methods with the ordinary Mock class::

    >>> from mock import Mock
    >>> 
    >>> mock = Mock()
    >>> mock.__str__ = Mock()
    >>> mock.__str__.return_value = 'wheeeeee'
    >>> str(mock)
    'wheeeeee'

* `mock on google code (repository and issue tracker) <http://code.google.com/p/mock/>`_
* `mock documentation <http://www.voidspace.org.uk/python/mock/>`_
* `mock on PyPI <http://pypi.python.org/pypi/mock/>`_
* `Article on mocking, patching and stubbing <http://www.voidspace.org.uk/python/articles/mocking.shtml>`_

