# Copyright (C) 2007-2011 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

from tests.support import unittest2

from mock import Mock, ANY, call, _spec_signature


class SomeClass(object):
    def one(self, a, b):
        pass
    def two(self):
        pass
    def three(self, a=None):
        pass



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

    def test_repr(self):
        self.assertEqual(repr(call), '<call>')
        self.assertEqual(str(call), '<call>')

        self.assertEqual(repr(call.foo), '<call foo>')

    def test_call(self):
        self.assertEqual(call(), ((), {}))
        self.assertEqual(call('foo', 'bar', one=3, two=4),
                         (('foo', 'bar'), {'one': 3, 'two': 4}))

        mock = Mock()
        mock(1, 2, 3)
        mock(a=3, b=6)
        self.assertEqual(mock.call_args_list,
                         [call(1, 2, 3), call(a=3, b=6)])

    def test_attribute_call(self):
        self.assertEqual(call.foo(1), ('foo', (1,), {}))
        self.assertEqual(call.bar.baz(fish='eggs'),
                         ('bar.baz', (), {'fish': 'eggs'}))

        mock = Mock()
        mock.foo(1, 2 ,3)
        mock.bar.baz(a=3, b=6)
        self.assertEqual(mock.method_calls,
                         [call.foo(1, 2, 3), call.bar.baz(a=3, b=6)])



class SpecSignatureTest(unittest2.TestCase):

    def test_basic(self):
        for spec in (SomeClass, SomeClass()):
            mock = _spec_signature(spec)

            self.assertRaises(AttributeError, getattr, mock, 'foo')
            mock.one(1, 2)
            mock.one.assert_called_with(1, 2)
            self.assertRaises(AssertionError,
                              mock.one.assert_called_with, 3, 4)
            self.assertRaises(TypeError, mock.one, 1)

            mock.two()
            mock.two.assert_called_with()
            self.assertRaises(AssertionError,
                              mock.two.assert_called_with, 3)
            self.assertRaises(TypeError, mock.two, 1)

            mock.three()
            mock.three.assert_called_with(None)
            self.assertRaises(AssertionError,
                              mock.three.assert_called_with, 3)
            self.assertRaises(TypeError, mock.three, 3, 2)

            mock.three(1)
            mock.three.assert_called_with(1)

            mock.three(a=1)
            mock.three.assert_called_with(1)


    def test_spec_as_list_fails(self):
        # should this fail or should the list be used as the spec?
        self.assertRaises(TypeError, _spec_signature, [])
        self.assertRaises(TypeError, _spec_signature, ['foo'])

        class Sub(list):
            pass

        mock = _spec_signature(Sub(['foo']))
        mock.append('bar')
        mock.append.assert_called_with('bar')


    def test_attributes(self):
        # test it is recursive - that class / instance attributes are mocked
        # with signatures
        pass


    def test_method_calls(self):
        # test method calls are recorded correctly in .method_calls
        pass


    def test_magic_methods(self):
        pass


    def test_spec_set(self):
        # a flag indicating whether or not spec_set should be used
        pass


    def test_property(self):
        pass


    def test_classmethod(self):
        pass


    def test_staticmethod(self):
        pass

