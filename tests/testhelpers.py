# Copyright (C) 2007-2011 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

from tests.support import unittest2

from mock import MagicMock, Mock, ANY, call, _spec_signature


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

    def _check_someclass_mock(self, mock):
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


    def test_basic(self):
        for spec in (SomeClass, SomeClass()):
            mock = _spec_signature(spec)
            self._check_someclass_mock(mock)


    def test_spec_as_list_fails(self):
        self.assertRaises(TypeError, _spec_signature, [])
        self.assertRaises(TypeError, _spec_signature, ['foo'])


    def test_attributes(self):
        class Sub(SomeClass):
            attr = SomeClass()

        sub_mock = _spec_signature(Sub)

        for mock in (sub_mock, sub_mock.attr):
            self._check_someclass_mock(mock)


    def test_builtin_functions_types(self):
        # we could replace builtin functions / methods with a mocksignature
        # with *args / **kwargs signature. Using the builtin method type
        # as a spec seems to work fairly well though.
        class BuiltinSubclass(list):
            def bar(self, arg):
                pass
            sorted = sorted
            attr = {}

        mock = _spec_signature(BuiltinSubclass)
        mock.append(3)
        mock.append.assert_called_with(3)
        self.assertRaises(AttributeError, getattr, mock.append, 'foo')

        mock.bar('foo')
        mock.bar.assert_called_with('foo')
        self.assertRaises(TypeError, mock.bar, 'foo', 'bar')
        self.assertRaises(AttributeError, getattr, mock.bar, 'foo')

        mock.sorted([1, 2])
        mock.sorted.assert_called_with([1, 2])
        self.assertRaises(AttributeError, getattr, mock.sorted, 'foo')

        mock.attr.pop(3)
        mock.attr.pop.assert_called_with(3)
        self.assertRaises(AttributeError, getattr, mock.attr, 'foo')


    def test_method_calls(self):
        class Sub(SomeClass):
            attr = SomeClass()

        mock = _spec_signature(Sub)
        mock.one(1, 2)
        mock.two()
        mock.three(3)

        expected = [call.one(1, 2), call.two(), call.three(3)]
        self.assertEqual(mock.method_calls, expected)

        mock.attr.one(1, 2)
        mock.attr.two()
        mock.attr.three(3)

        expected.extend(
            [call.attr.one(1, 2), call.attr.two(), call.attr.three(3)]
        )
        self.assertEqual(mock.method_calls, expected)


    def test_magic_methods(self):
        class BuiltinSubclass(list):
            attr = {}

        mock = _spec_signature(BuiltinSubclass)
        self.assertEqual(list(mock), [])
        self.assertRaises(TypeError, int, mock)
        self.assertRaises(TypeError, int, mock.attr)
        self.assertEqual(list(mock), [])

        self.assertIsInstance(mock['foo'], MagicMock)
        self.assertIsInstance(mock.attr['foo'], MagicMock)


    def test_spec_set(self):
        class Sub(SomeClass):
            attr = SomeClass()

        for spec in (Sub, Sub()):
            mock = _spec_signature(spec, spec_set=True)
            self._check_someclass_mock(mock)

            self.assertRaises(AttributeError, setattr, mock, 'foo', 'bar')
            self.assertRaises(AttributeError, setattr, mock.attr, 'foo', 'bar')


    def test_classmethod(self):
        class Foo(object):
            @classmethod
            def f(cls, a, b):
                pass

        class Bar(Foo):
            pass

        for spec in (Foo, Foo(), Bar, Bar()):
            mock = _spec_signature(spec)
            mock.f(1, 2)
            mock.f.assert_called_with(1, 2)


    def test_staticmethod(self):
        class Foo(object):
            @staticmethod
            def f(a, b):
                pass

        class Bar(Foo):
            pass

        for spec in (Foo, Foo(), Bar, Bar()):
            mock = _spec_signature(spec)
            mock.f(1, 2)
            mock.f.assert_called_with(1, 2)
