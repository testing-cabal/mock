# Copyright (C) 2007-2011 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

from tests.support import unittest2, inPy3k

from mock import MagicMock, Mock, ANY, call, create_autospec


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
        mock.three.assert_called_with()
        self.assertRaises(AssertionError,
                          mock.three.assert_called_with, 3)
        self.assertRaises(TypeError, mock.three, 3, 2)

        mock.three(1)
        mock.three.assert_called_with(1)

        mock.three(a=1)
        mock.three.assert_called_with(a=1)


    def test_basic(self):
        for spec in (SomeClass, SomeClass()):
            mock = create_autospec(spec)
            self._check_someclass_mock(mock)


    def test_function_as_instance_attribute(self):
        obj = SomeClass()
        def f(a):
            pass
        obj.f = f

        mock = create_autospec(obj)
        mock.f('bing')
        mock.f.assert_called_with('bing')


    def test_spec_as_list(self):
        # because spec as a list of strings in the mock constructor means
        # something very different we treat a list instance as the type.
        mock = create_autospec([])
        mock.append('foo')
        mock.append.assert_called_with('foo')

        self.assertRaises(AttributeError, getattr, mock, 'foo')

        class Foo(object):
            foo = []

        mock = create_autospec(Foo)
        mock.foo.append(3)
        mock.foo.append.assert_called_with(3)
        self.assertRaises(AttributeError, getattr, mock.foo, 'foo')


    def test_attributes(self):
        class Sub(SomeClass):
            attr = SomeClass()

        sub_mock = create_autospec(Sub)

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

        mock = create_autospec(BuiltinSubclass)
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

        mock = create_autospec(Sub)
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

        mock = create_autospec(BuiltinSubclass)
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
            mock = create_autospec(spec, spec_set=True)
            self._check_someclass_mock(mock)

            self.assertRaises(AttributeError, setattr, mock, 'foo', 'bar')
            self.assertRaises(AttributeError, setattr, mock.attr, 'foo', 'bar')


    def test_descriptors(self):
        class Foo(object):
            @classmethod
            def f(cls, a, b):
                pass
            @staticmethod
            def g(a, b):
                pass

        class Bar(Foo):
            pass

        class Baz(SomeClass, Bar):
            pass

        for spec in (Foo, Foo(), Bar, Bar(), Baz, Baz()):
            mock = create_autospec(spec)
            mock.f(1, 2)
            mock.f.assert_called_once_with(1, 2)

            mock.g(3, 4)
            mock.g.assert_called_once_with(3, 4)


    @unittest2.skipIf(inPy3k, "No old style classes in Python 3")
    def test_old_style_classes(self):
        class Foo:
            def f(self, a, b):
                pass

        class Bar(Foo):
            g = Foo()

        for spec in (Foo, Foo(), Bar, Bar()):
            mock = create_autospec(spec)
            mock.f(1, 2)
            mock.f.assert_called_once_with(1, 2)

            self.assertRaises(AttributeError, getattr, mock, 'foo')
            self.assertRaises(AttributeError, getattr, mock.f, 'foo')

        mock.g.f(1, 2)
        mock.g.f.assert_called_once_with(1, 2)
        self.assertRaises(AttributeError, getattr, mock.g, 'foo')


    def test_recursive(self):
        class A(object):
            def a(self):
                pass
            foo = 'foo bar baz'
            bar = foo

        A.B = A
        mock = create_autospec(A)

        mock()
        self.assertFalse(mock.B.called)

        mock.a()
        mock.B.a()
        self.assertEqual(mock.method_calls, [call.a(), call.B.a()])

        self.assertIs(A.foo, A.bar)
        self.assertIsNot(mock.foo, mock.bar)
        mock.foo.lower()
        self.assertRaises(AssertionError, mock.bar.lower.assert_called_with)


    def test_spec_inheritance_for_classes(self):
        class Foo(object):
            def a(self):
                pass
            class Bar(object):
                def f(self):
                    pass

        class_mock = create_autospec(Foo)

        self.assertIsNot(class_mock, class_mock())

        for this_mock in class_mock, class_mock():
            this_mock.a()
            this_mock.a.assert_called_with()
            self.assertRaises(TypeError, this_mock.a, 'foo')
            self.assertRaises(AttributeError, getattr, this_mock, 'b')

        instance_mock = create_autospec(Foo())
        instance_mock.a()
        instance_mock.a.assert_called_with()
        self.assertRaises(TypeError, instance_mock.a, 'foo')
        self.assertRaises(AttributeError, getattr, instance_mock, 'b')

        # The return value isn't isn't callable
        self.assertRaises(TypeError, instance_mock)

        instance_mock.Bar.f()
        instance_mock.Bar.f.assert_called_with()
        self.assertRaises(AttributeError, getattr, instance_mock.Bar, 'g')

        instance_mock.Bar().f()
        instance_mock.Bar().f.assert_called_with()
        self.assertRaises(AttributeError, getattr, instance_mock.Bar(), 'g')


    def test_inherit(self):
        class Foo(object):
            a = 3

        Foo.Foo = Foo

        # class
        mock = create_autospec(Foo)
        instance = mock()
        self.assertRaises(AttributeError, getattr, instance, 'b')

        attr_instance = mock.Foo()
        self.assertRaises(AttributeError, getattr, attr_instance, 'b')

        # instance
        mock = create_autospec(Foo())
        self.assertRaises(AttributeError, getattr, mock, 'b')
        self.assertRaises(TypeError, mock)

        # attribute instance
        call_result = mock.Foo()
        self.assertRaises(AttributeError, getattr, call_result, 'b')


    def test_builtins(self):
        # used to fail with infinite recursion
        create_autospec(1)

        create_autospec(int)
        create_autospec('foo')
        create_autospec(str)
        create_autospec({})
        create_autospec(dict)
        create_autospec([])
        create_autospec(list)
        create_autospec(set())
        create_autospec(set)
        create_autospec(1.0)
        create_autospec(float)
        create_autospec(1j)
        create_autospec(complex)
        create_autospec(False)
        create_autospec(True)


    def test_function(self):
        def f(a, b):
            pass

        mock = create_autospec(f)
        self.assertRaises(TypeError, mock)
        mock(1, 2)
        mock.assert_called_with(1, 2)

        f.f = f
        mock = create_autospec(f)
        self.assertRaises(TypeError, mock.f)
        mock.f(3, 4)
        mock.f.assert_called_with(3, 4)


    def test_signature_class(self):
        class Foo(object):
            def __init__(self, a, b=3):
                pass

        mock = create_autospec(Foo)

        self.assertRaises(TypeError, mock)
        mock(1)
        mock.assert_called_once_with(1)

        mock(4, 5)
        mock.assert_called_with(4, 5)


    @unittest2.skipIf(inPy3k, 'no old style classes in Python 3')
    def test_signature_old_style_class(self):
        class Foo:
            def __init__(self, a, b=3):
                pass

        mock = create_autospec(Foo)

        self.assertRaises(TypeError, mock)
        mock(1)
        mock.assert_called_once_with(1)

        mock(4, 5)
        mock.assert_called_with(4, 5)


    def test_class_with_no_init(self):
        # this used to raise an exception
        # due to trying to get a signature from object.__init__
        class Foo(object):
            pass
        create_autospec(Foo)


    @unittest2.skipIf(inPy3k, 'no old style classes in Python 3')
    def test_old_style_class_with_no_init(self):
        # this used to raise an exception
        # due to Foo.__init__ raising an AttributeError
        class Foo:
            pass
        create_autospec(Foo)


    def test_signature_callable(self):
        class Callable(object):
            def __init__(self):
                pass
            def __call__(self, a):
                pass

        mock = create_autospec(Callable)
        mock()
        mock.assert_called_once_with()
        self.assertRaises(TypeError, mock, 'a')

        mock = create_autospec(Callable())
        mock(a='a')
        mock.assert_called_once_with(a='a')
        self.assertRaises(TypeError, mock)


    def test_create_autospec_none(self):
        class Foo(object):
            bar = None

        mock = create_autospec(Foo)
        none = mock.bar
        self.assertNotIsInstance(none, type(None))

        none.foo()
        none.foo.assert_called_once_with()


    def test_autospec_functions_with_self_in_odd_place(self):
        class Foo(object):
            def f(a, self):
                pass

        a = create_autospec(Foo)
        a.f(self=10)
        a.f.assert_called_with(self=10)


    def test_autospec_property(self):
        class Foo(object):
            @property
            def foo(self):
                return 3

        foo = create_autospec(Foo)
        mock_property = foo.foo

        # no spec on properties
        self.assertTrue(isinstance(mock_property, MagicMock))
        mock_property(1, 2, 3)
        mock_property.abc(4, 5, 6)
        mock_property.assert_called_once_with(1, 2, 3)
        mock_property.abc.assert_called_once_with(4, 5, 6)

