# Copyright (C) 2007-2011 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

from tests.support import unittest2, inPy3k

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


    def test_function_as_instance_attribute(self):
        obj = SomeClass()
        def f(a):
            pass
        obj.f = f

        mock = _spec_signature(obj)
        mock.f('bing')
        mock.f.assert_called_with('bing')


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
            mock = _spec_signature(spec)
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
            mock = _spec_signature(spec)
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
        mock = _spec_signature(A)

        self.assertIs(mock, mock.B)
        self.assertIs(mock.a, mock.B.a)

        # XXXX note that the mock names (and therefore entries in method_calls)
        #      will be incorrect for cached entries
        mock.a()
        mock.B.a()
        self.assertEqual(mock.method_calls, [call.a(), call.a()])

        # builtin types should not be cached
        self.assertIs(A.foo, A.bar)
        self.assertIsNot(mock.foo, mock.bar)
        mock.foo.lower()
        self.assertRaises(AssertionError, mock.bar.assert_called_with)

        # create a function with the same id and test that it is treated
        # differently rather than the mock reused
        A.b = A.__dict__['a']
        mock = _spec_signature(A)
        self.assertIsNot(mock.a, mock.b)

        mock.b()
        mock.b.assert_called_with()
        self.assertRaises(AssertionError, mock.a.assert_called_with)

        ## Note: functions that have themselves as attributes, even indirectly,
        ##       still fail. Unfortunate. We don't want to cache functions
        ##       though, as we need to treat them differently if found on a
        ##       class to if found on their own. So we can't cache just based on
        ##       id.
        #def f():
        #    pass
        #f.a = f
        #mock = _spec_signature(f)


    def test_spec_inheritance_for_classes(self):
        class Foo(object):
            def a(self):
                pass
            class Bar(object):
                class Baz(object):
                    pass
                def f(self):
                    pass

        class_mock = _spec_signature(Foo, inherit=True)

        self.assertIsNot(class_mock, class_mock())

        for this_mock in class_mock, class_mock():
            this_mock.a()
            this_mock.a.assert_called_with()
            self.assertRaises(TypeError, this_mock.a, 'foo')
            self.assertRaises(AttributeError, getattr, this_mock, 'b')

        self.assertIs(class_mock.Bar, class_mock().Bar)
        self.assertIsNot(class_mock.a, class_mock().a)

        instance_mock = _spec_signature(Foo(), inherit=True)
        instance_mock.a()
        instance_mock.a.assert_called_with()
        self.assertRaises(TypeError, instance_mock.a, 'foo')
        self.assertRaises(AttributeError, getattr, instance_mock, 'b')

        # The return value isn't created with a spec because the spec is an
        # instance and not a class. The spec isn't inherited by return value.
        instance_mock().a(1, 2, 3)
        instance_mock().a.assert_called_with(1, 2, 3)

        self.assertIs(instance_mock.Bar.Baz, instance_mock.Bar().Baz)
        self.assertIsNot(instance_mock.Bar.f, instance_mock.Bar().f)


    def test_builtins(self):
        # used to fail with infinite recursion
        _spec_signature(1)

        _spec_signature(int)
        _spec_signature('foo')
        _spec_signature(str)
        _spec_signature({})
        _spec_signature(dict)
        _spec_signature(list)
        _spec_signature(set())
        _spec_signature(set)
        _spec_signature(1.0)
        _spec_signature(float)
        _spec_signature(1j)
        _spec_signature(complex)
        _spec_signature(False)
        _spec_signature(True)


    def test_none(self):
        # used to fail because it's the default value of Mock spec arg
        mock = _spec_signature(None)
        self.assertRaises(AttributeError, getattr, mock, 'foo')


    def test_spec_inheritance_callables(self):
        # with spec inheritance we could mock classes __init__ and callable
        # object signatures with mocksignature.
        # how does mocksignature on a class with no __init__ method work?
        # (i.e. will inherit object.__init__ that takes no args but implemented
        #  in C.)

        # could we mock callable object signatures anyway - without requiring
        # inheritance?
        # for classes that are attributes we could inherit - it is only for
        # top level classes that we can't know if they may be used as
        # instances.

        # for classes
        pass
