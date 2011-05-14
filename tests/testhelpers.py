# Copyright (C) 2007-2011 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

from tests.support import unittest2

from mock import Mock, ANY, call


class AnyTest(unittest2.TestCase):

    def test_any(self):
        self.assertEqual(ANY, object())

        mock = Mock()
        mock(ANY)
        mock.assert_called_with(ANY)

        mock = Mock()
        mock(foo=ANY)
        mock.assert_called_with(foo=ANY)

    def test_repr(self):
        self.assertEqual(repr(ANY), '<ANY>')
        self.assertEqual(str(ANY), '<ANY>')



class CallTest(unittest2.TestCase):
    """
    >>> mock = Mock(return_value=None)
    >>> mock(1, 2, 3)
    >>> mock(a=3, b=6)
    >>> mock.call_args_list == [call(1, 2, 3), call(a=3, b=6)]
    True

    >>> mock = Mock()
    >>> mock.foo(1, 2 ,3)
    <mock.Mock object at 0x...>
    >>> mock.bar.baz(a=3, b=6)
    <mock.Mock object at 0x...>
    >>> mock.method_calls == [call.foo(1, 2, 3), call.bar.baz(a=3, b=6)]
    True

And for good measure, the first example (tracking order of calls between
mocks) using the new `call` object for assertions:

.. doctest::

    >>> manager = Mock()

    >>> mock_foo = manager.foo
    >>> mock_bar = manager.bar

    >>> mock_foo.something()
    <mock.Mock object at 0x...>
    >>> mock_bar.other.thing()
    <mock.Mock object at 0x...>

    >>> manager.method_calls == [call.foo.something(), call.bar.other.thing()]
    True
    """

    def test_repr(self):
        self.assertEqual(repr(call), '<call>')
        self.assertEqual(str(call), '<call>')

        self.assertEqual(repr(call.foo), '<call foo>')

    def test_call(self):
        self.assertEqual(call(), ((), {}))
        self.assertEqual(call('foo', 'bar', one=3, two=4),
                         (('foo', 'bar'), {'one': 3, 'two': 4}))
