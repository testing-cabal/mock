# Copyright (C) 2007-2012 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

import inspect

from tests.support import unittest2

from mock import Mock, mocksignature, patch


class Something(object):
    def __init__(self, foo, bar=10):
        pass
    def __call__(self, foo, bar=5):
        pass

something = Something(1, 2)


def f(a, b, c):
    pass


class TestMockSignature(unittest2.TestCase):

    def test_function(self):
        def f(a):
            pass
        mock = Mock()

        f2  = mocksignature(f, mock)
        self.assertIs(f2.mock, mock)

        self.assertRaises(TypeError, f2)
        mock.return_value = 3
        self.assertEqual(f2('foo'), 3)
        mock.assert_called_with('foo')
        f2.mock.assert_called_with('foo')


    def test_function_without_explicit_mock(self):
        def f(a):
            pass

        f2  = mocksignature(f)
        self.assertIsInstance(f2.mock, Mock)

        self.assertRaises(TypeError, f2)
        f2.mock.return_value = 3
        self.assertEqual(f2('foo'), 3)
        f2.mock.assert_called_with('foo')


    def test_method(self):
        class Foo(object):
            def method(self, a, b):
                pass

        f = Foo()
        mock = Mock()
        mock.return_value = 3
        f.method = mocksignature(f.method, mock)
        self.assertEqual(f.method('foo', 'bar'), 3)
        mock.assert_called_with('foo', 'bar')


    def test_function_with_defaults(self):
        def f(a, b=None):
            pass
        mock = Mock()
        f2  = mocksignature(f, mock)
        f2(3)
        mock.assert_called_with(3, None)
        mock.reset_mock()

        f2(1, 7)
        mock.assert_called_with(1, 7)
        mock.reset_mock()

        f2(b=1, a=7)
        mock.assert_called_with(7, 1)
        mock.reset_mock()

        a = object()
        def f(a=a):
            pass
        f2 = mocksignature(f, mock)
        f2()
        mock.assert_called_with(a)


    def test_introspection(self):
        def f(a, *args, **kwargs):
            pass
        f2 = mocksignature(f, f)
        self.assertEqual(inspect.getargspec(f), inspect.getargspec(f2))

        def f(a, b=None, c=3, d=object()):
            pass
        f2 = mocksignature(f, f)
        self.assertEqual(inspect.getargspec(f), inspect.getargspec(f2))


    def test_function_with_varargs_and_kwargs(self):
        def f(a, b=None, *args, **kwargs):
            return (a, b, args, kwargs)
        f2 = mocksignature(f, f)
        self.assertEqual(f2(3, 4, 5, x=6, y=9), (3, 4, (5,), {'x': 6, 'y': 9}))
        self.assertEqual(f2(3, x=6, y=9, b='a'), (3, 'a', (), {'x': 6, 'y': 9}))

        def f(*args):
            pass
        g = mocksignature(f)
        g.mock.return_value = 3
        self.assertEqual(g(1, 2, 'many'), 3)
        self.assertEqual(g(), 3)
        self.assertRaises(TypeError, lambda: g(a=None))

        def f(**kwargs):
            pass
        g = mocksignature(f)
        g.mock.return_value = 3
        self.assertEqual(g(), 3)
        self.assertEqual(g(a=None, b=None), 3)
        self.assertRaises(TypeError, lambda: g(None))


    def test_mocksignature_with_patch(self):
        mock = Mock()

        def f(a, b, c):
            pass
        mock.f = f

        @patch.object(mock, 'f', mocksignature=True)
        def test(mock_f):
            self.assertRaises(TypeError, mock.f, 3, 4)
            self.assertRaises(TypeError, mock.f, 3, 4, 5, 6)
            mock.f(1, 2, 3)

            mock_f.assert_called_with(1, 2, 3)
            mock.f.mock.assert_called_with(1, 2, 3)

        test()

        @patch('tests.support.SomeClass.wibble', mocksignature=True)
        def test(mock_wibble):
            from tests.support import SomeClass

            instance = SomeClass()
            self.assertRaises(TypeError, instance.wibble, 1)
            instance.wibble()

            mock_wibble.assert_called_with(instance)
            instance.wibble.mock.assert_called_with(instance)

        test()


    @unittest2.skipUnless(__debug__, 'assert disabled when run with -O/OO')
    def test_mocksignature_with_reserved_arg(self):
        def f(_mock_):
            pass
        self.assertRaises(AssertionError, lambda: mocksignature(f))

        def f(_mock_=None):
            pass
        self.assertRaises(AssertionError, lambda: mocksignature(f))

        def f(*_mock_):
            pass
        self.assertRaises(AssertionError, lambda: mocksignature(f))

        def f(**_mock_):
            pass
        self.assertRaises(AssertionError, lambda: mocksignature(f))


    def test_mocksignature_class(self):
        MockedSomething = mocksignature(Something)

        result = MockedSomething(5, 23)
        self.assertIs(result, MockedSomething.mock.return_value)

        MockedSomething(1)
        MockedSomething.mock.assert_caled_with(1, 10)

        self.assertRaises(TypeError, MockedSomething)


    def test_mocksignature_callable(self):
        mocked_something = mocksignature(something)

        result = mocked_something(5, 23)
        self.assertIs(result, mocked_something.mock.return_value)

        mocked_something(1)
        mocked_something.mock.assert_caled_with(1, 5)

        self.assertRaises(TypeError, mocked_something)


    def test_patch_mocksignature_class(self):
        original_something = Something
        something_name = '%s.Something' % __name__
        @patch(something_name, mocksignature=True)
        def test(MockSomething):
            Something(3, 5)
            MockSomething.assert_called_with(3, 5)

            Something(6)
            MockSomething.assert_called_with(6, 10)

            self.assertRaises(TypeError, Something)
        test()
        self.assertIs(Something, original_something)


    def test_patch_mocksignature_callable(self):
        original_something = something
        something_name = '%s.something' % __name__
        @patch(something_name, mocksignature=True)
        def test(MockSomething):
            something(3, 4)
            MockSomething.assert_called_with(3, 4)

            something(6)
            MockSomething.assert_called_with(6, 5)

            self.assertRaises(TypeError, something)
        test()
        self.assertIs(something, original_something)


    def test_patchobject_mocksignature(self):
        class something(object):
            def meth(self, a, b, c):
                pass

        original = something.__dict__['meth']

        @patch.object(something, 'meth', mocksignature=True)
        def test(_):
            self.assertIsNot(something.__dict__['meth'], original)
            thing = something()
            thing.meth(1, 2, 3)
            self.assertRaises(TypeError, thing.meth, 1)

        test()
        self.assertIs(something.__dict__['meth'], original)

        thing = something()

        original = thing.meth
        @patch.object(thing, 'meth', mocksignature=True)
        def test(_):
            thing.meth(1, 2, 3)
            self.assertRaises(TypeError, thing.meth, 1)

        test()
        self.assertEqual(thing.meth, original)

        # when patching instance methods using mocksignatures we used to
        # replace the bound method with an instance attribute on unpatching.
        self.assertNotIn('meth', thing.__dict__)


    def test_assert_called_with(self):
        func = mocksignature(f)

        self.assertRaises(AssertionError, func.assert_called_with)
        self.assertRaises(AssertionError, func.assert_called_once_with)

        func(1, 2, 3)
        func.assert_called_with(1, 2, 3)
        self.assertRaises(AssertionError, func.assert_called_with, 4, 5, 6)
        func.assert_called_once_with(1, 2, 3)
        self.assertRaises(AssertionError, func.assert_called_once_with,
                          4, 5, 6)


    def test_mock_attributes(self):
        func = mocksignature(f)

        return_value = func.return_value
        self.assertIsInstance(return_value, Mock)
        self.assertIsNone(func.side_effect)
        self.assertFalse(func.called)
        self.assertIsNone(func.call_args)
        self.assertEqual(func.call_count, 0)
        self.assertEqual(func.method_calls, [])
        self.assertEqual(func.call_args_list, [])
        self.assertIs(func._mock_children, func.mock._mock_children)

        self.assertIs(func(1, 2, 3), return_value)

        self.assertTrue(func.called)
        self.assertEqual(func.call_args, ((1, 2, 3), {}))
        self.assertEqual(func.call_count, 1)
        self.assertEqual(func.method_calls, [])
        self.assertEqual(func.call_args_list, [((1, 2, 3), {})])
        func.method_calls.append('foo')

        return_value()
        func.reset_mock()

        self.assertEqual(return_value.call_count, False)
        self.assertFalse(func.called)
        self.assertIsNone(func.call_args)
        self.assertEqual(func.call_count, 0)
        self.assertEqual(func.method_calls, [])
        self.assertEqual(func.call_args_list, [])
        self.assertIs(func._mock_children, func.mock._mock_children)

        func.side_effect = KeyError
        self.assertRaises(KeyError, func, 1, 2, 3)
        self.assertTrue(func.called)

        func.side_effect = None
        func.return_value = 'foo'
        self.assertEqual(func(1, 2, 3), 'foo')
        self.assertEqual(func.call_count, 2)


    def test_return_value_from_existing_mock(self):
        mock = Mock(return_value='foo')
        func = mocksignature(f, mock)
        self.assertEqual(func(1, 2, 3), 'foo')

        mock.return_value = 'bar'
        self.assertEqual(func(1, 2, 3), 'bar')


    def test_side_effect_from_existing_mock(self):
        mock = Mock(side_effect=KeyError)
        func = mocksignature(f, mock)
        self.assertRaises(KeyError, func, 1, 2, 3)

        mock.side_effect = NameError
        self.assertRaises(NameError, func, 1, 2, 3)


if __name__ == '__main__':
    unittest2.main()
