# Copyright (C) 2007-2011 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

import os
import sys

from tests import support
from tests.support import unittest2, inPy3k, SomeClass, is_instance

from mock import (
    NonCallableMock, CallableMixin, patch, sentinel,
    MagicMock, Mock, NonCallableMagicMock, patch
)

builtin_string = '__builtin__'
if inPy3k:
    builtin_string = 'builtins'

PTModule = sys.modules[__name__]


def _get_proxy(obj, get_only=True):
    class Proxy(object):
        def __getattr__(self, name):
            return getattr(obj, name)
    if not get_only:
        def __setattr__(self, name, value):
            setattr(obj, name, value)
        def __delattr__(self, name):
            delattr(obj, name)
        Proxy.__setattr__ = __setattr__
        Proxy.__delattr__ = __delattr__
    return Proxy()


# for use in the test
something  = sentinel.Something
something_else  = sentinel.SomethingElse


class Foo(object):
    def __init__(self, a):
        pass
    def f(self, a):
        pass
    def g(self):
        pass
    foo = 'bar'

    class Bar(object):
        def a(self):
            pass

foo_name = '%s.Foo' % __name__


def function(a, b=Foo):
    pass


class Container(object):
    def __init__(self):
        self.values = {}

    def __getitem__(self, name):
        return self.values[name]

    def __setitem__(self, name, value):
        self.values[name] = value

    def __delitem__(self, name):
        del self.values[name]

    def __iter__(self):
        return iter(self.values)



class PatchTest(unittest2.TestCase):

    def assertNotCallable(self, obj, magic=True):
        MockClass = NonCallableMagicMock
        if not magic:
            MockClass = NonCallableMock

        self.assertRaises(TypeError, obj)
        self.assertTrue(is_instance(obj, MockClass))
        self.assertFalse(is_instance(obj, CallableMixin))


    def test_single_patchobject(self):
        class Something(object):
            attribute = sentinel.Original

        @patch.object(Something, 'attribute', sentinel.Patched)
        def test():
            self.assertEqual(Something.attribute, sentinel.Patched, "unpatched")

        test()
        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch not restored")


    def test_patchobject_with_none(self):
        class Something(object):
            attribute = sentinel.Original

        @patch.object(Something, 'attribute', None)
        def test():
            self.assertIsNone(Something.attribute, "unpatched")

        test()
        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch not restored")


    def test_multiple_patchobject(self):
        class Something(object):
            attribute = sentinel.Original
            next_attribute = sentinel.Original2

        @patch.object(Something, 'attribute', sentinel.Patched)
        @patch.object(Something, 'next_attribute', sentinel.Patched2)
        def test():
            self.assertEqual(Something.attribute, sentinel.Patched,
                             "unpatched")
            self.assertEqual(Something.next_attribute, sentinel.Patched2,
                             "unpatched")

        test()
        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch not restored")
        self.assertEqual(Something.next_attribute, sentinel.Original2,
                         "patch not restored")


    def test_object_lookup_is_quite_lazy(self):
        global something
        original = something
        @patch('tests.testpatch.something', sentinel.Something2)
        def test():
            pass

        try:
            something = sentinel.replacement_value
            test()
            self.assertEqual(something, sentinel.replacement_value)
        finally:
            something = original


    def test_patch(self):
        @patch('%s.something' % __name__, sentinel.Something2)
        def test():
            self.assertEqual(PTModule.something, sentinel.Something2,
                             "unpatched")

        test()
        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch not restored")

        @patch('tests.testpatch.something', sentinel.Something2)
        @patch('tests.testpatch.something_else', sentinel.SomethingElse)
        def test():
            self.assertEqual(PTModule.something, sentinel.Something2,
                             "unpatched")
            self.assertEqual(PTModule.something_else, sentinel.SomethingElse,
                             "unpatched")

        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch not restored")
        self.assertEqual(PTModule.something_else, sentinel.SomethingElse,
                         "patch not restored")

        # Test the patching and restoring works a second time
        test()

        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch not restored")
        self.assertEqual(PTModule.something_else, sentinel.SomethingElse,
                         "patch not restored")

        mock = Mock()
        mock.return_value = sentinel.Handle
        @patch('%s.open' % builtin_string, mock)
        def test():
            self.assertEqual(open('filename', 'r'), sentinel.Handle,
                             "open not patched")
        test()
        test()

        self.assertNotEqual(open, mock, "patch not restored")


    def test_patch_class_attribute(self):
        @patch('tests.testpatch.SomeClass.class_attribute',
               sentinel.ClassAttribute)
        def test():
            self.assertEqual(PTModule.SomeClass.class_attribute,
                             sentinel.ClassAttribute, "unpatched")
        test()

        self.assertIsNone(PTModule.SomeClass.class_attribute,
                          "patch not restored")


    def test_patchobject_with_default_mock(self):
        class Test(object):
            something = sentinel.Original
            something2 = sentinel.Original2

        @patch.object(Test, 'something')
        def test(mock):
            self.assertEqual(mock, Test.something,
                             "Mock not passed into test function")
            self.assertIsInstance(mock, MagicMock,
                            "patch with two arguments did not create a mock")

        test()

        @patch.object(Test, 'something')
        @patch.object(Test, 'something2')
        def test(this1, this2, mock1, mock2):
            self.assertEqual(this1, sentinel.this1,
                             "Patched function didn't receive initial argument")
            self.assertEqual(this2, sentinel.this2,
                             "Patched function didn't receive second argument")
            self.assertEqual(mock1, Test.something2,
                             "Mock not passed into test function")
            self.assertEqual(mock2, Test.something,
                             "Second Mock not passed into test function")
            self.assertIsInstance(mock2, MagicMock,
                            "patch with two arguments did not create a mock")
            self.assertIsInstance(mock2, MagicMock,
                            "patch with two arguments did not create a mock")

            # A hack to test that new mocks are passed the second time
            self.assertNotEqual(outerMock1, mock1, "unexpected value for mock1")
            self.assertNotEqual(outerMock2, mock2, "unexpected value for mock1")
            return mock1, mock2

        outerMock1 = outerMock2 = None
        outerMock1, outerMock2 = test(sentinel.this1, sentinel.this2)

        # Test that executing a second time creates new mocks
        test(sentinel.this1, sentinel.this2)


    def test_patch_with_spec(self):
        @patch('tests.testpatch.SomeClass', spec=SomeClass)
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertTrue(is_instance(SomeClass.wibble, MagicMock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)

        test()


    def test_patchobject_with_spec(self):
        @patch.object(SomeClass, 'class_attribute', spec=SomeClass)
        def test(MockAttribute):
            self.assertEqual(SomeClass.class_attribute, MockAttribute)
            self.assertTrue(is_instance(SomeClass.class_attribute.wibble,
                                       MagicMock))
            self.assertRaises(AttributeError,
                              lambda: SomeClass.class_attribute.not_wibble)

        test()


    def test_patch_with_spec_as_list(self):
        @patch('tests.testpatch.SomeClass', spec=['wibble'])
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertTrue(is_instance(SomeClass.wibble, MagicMock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)

        test()


    def test_patchobject_with_spec_as_list(self):
        @patch.object(SomeClass, 'class_attribute', spec=['wibble'])
        def test(MockAttribute):
            self.assertEqual(SomeClass.class_attribute, MockAttribute)
            self.assertTrue(is_instance(SomeClass.class_attribute.wibble,
                                       MagicMock))
            self.assertRaises(AttributeError,
                              lambda: SomeClass.class_attribute.not_wibble)

        test()


    def test_nested_patch_with_spec_as_list(self):
        # regression test for nested decorators
        @patch('%s.open' % builtin_string)
        @patch('tests.testpatch.SomeClass', spec=['wibble'])
        def test(MockSomeClass, MockOpen):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertTrue(is_instance(SomeClass.wibble, MagicMock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)
        test()


    def test_patch_with_spec_as_boolean(self):
        @patch('tests.testpatch.SomeClass', spec=True)
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            # Should not raise attribute error
            MockSomeClass.wibble

            self.assertRaises(AttributeError, lambda: MockSomeClass.not_wibble)

        test()


    def test_patch_object_with_spec_as_boolean(self):
        from tests import testpatch
        @patch.object(testpatch, 'SomeClass', spec=True)
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            # Should not raise attribute error
            MockSomeClass.wibble

            self.assertRaises(AttributeError, lambda: MockSomeClass.not_wibble)

        test()


    def test_patch_class_acts_with_spec_is_inherited(self):
        @patch('tests.testpatch.SomeClass', spec=True)
        def test(MockSomeClass):
            self.assertTrue(is_instance(MockSomeClass, MagicMock))
            instance = MockSomeClass()
            self.assertNotCallable(instance)
            # Should not raise attribute error
            instance.wibble

            self.assertRaises(AttributeError, lambda: instance.not_wibble)

        test()


    def test_patch_with_create_mocks_non_existent_attributes(self):
        @patch('%s.frooble' % builtin_string, sentinel.Frooble, create=True)
        def test():
            self.assertEqual(frooble, sentinel.Frooble)

        test()
        self.assertRaises(NameError, lambda: frooble)


    def test_patchobject_with_create_mocks_non_existent_attributes(self):
        @patch.object(SomeClass, 'frooble', sentinel.Frooble, create=True)
        def test():
            self.assertEqual(SomeClass.frooble, sentinel.Frooble)

        test()
        self.assertFalse(hasattr(SomeClass, 'frooble'))


    def test_patch_wont_create_by_default(self):
        try:
            @patch('%s.frooble' % builtin_string, sentinel.Frooble)
            def test():
                self.assertEqual(frooble, sentinel.Frooble)

            test()
        except AttributeError:
            pass
        else:
            self.fail('Patching non existent attributes should fail')

        self.assertRaises(NameError, lambda: frooble)


    def test_patchobject_wont_create_by_default(self):
        try:
            @patch.object(SomeClass, 'frooble', sentinel.Frooble)
            def test():
                self.fail('Patching non existent attributes should fail')

            test()
        except AttributeError:
            pass
        else:
            self.fail('Patching non existent attributes should fail')
        self.assertFalse(hasattr(SomeClass, 'frooble'))


    def test_patch_with_static_methods(self):
        class Foo(object):
            @staticmethod
            def woot():
                return sentinel.Static

        @patch.object(Foo, 'woot', staticmethod(lambda: sentinel.Patched))
        def anonymous():
            self.assertEqual(Foo.woot(), sentinel.Patched)
        anonymous()

        self.assertEqual(Foo.woot(), sentinel.Static)


    def test_patch_local(self):
        foo = sentinel.Foo
        @patch.object(sentinel, 'Foo', 'Foo')
        def anonymous():
            self.assertEqual(sentinel.Foo, 'Foo')
        anonymous()

        self.assertEqual(sentinel.Foo, foo)


    def test_patch_slots(self):
        class Foo(object):
            __slots__ = ('Foo',)

        foo = Foo()
        foo.Foo = sentinel.Foo

        @patch.object(foo, 'Foo', 'Foo')
        def anonymous():
            self.assertEqual(foo.Foo, 'Foo')
        anonymous()

        self.assertEqual(foo.Foo, sentinel.Foo)


    def test_patchobject_class_decorator(self):
        class Something(object):
            attribute = sentinel.Original

        class Foo(object):
            def test_method(other_self):
                self.assertEqual(Something.attribute, sentinel.Patched,
                                 "unpatched")
            def not_test_method(other_self):
                self.assertEqual(Something.attribute, sentinel.Original,
                                 "non-test method patched")

        Foo = patch.object(Something, 'attribute', sentinel.Patched)(Foo)

        f = Foo()
        f.test_method()
        f.not_test_method()

        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch not restored")


    def test_patch_class_decorator(self):
        class Something(object):
            attribute = sentinel.Original

        class Foo(object):
            def test_method(other_self, mock_something):
                self.assertEqual(PTModule.something, mock_something,
                                 "unpatched")
            def not_test_method(other_self):
                self.assertEqual(PTModule.something, sentinel.Something,
                                 "non-test method patched")
        Foo = patch('%s.something' % __name__)(Foo)

        f = Foo()
        f.test_method()
        f.not_test_method()

        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch not restored")
        self.assertEqual(PTModule.something, sentinel.Something,
                         "patch not restored")


    def test_patchobject_twice(self):
        class Something(object):
            attribute = sentinel.Original
            next_attribute = sentinel.Original2

        @patch.object(Something, 'attribute', sentinel.Patched)
        @patch.object(Something, 'attribute', sentinel.Patched)
        def test():
            self.assertEqual(Something.attribute, sentinel.Patched, "unpatched")

        test()

        self.assertEqual(Something.attribute, sentinel.Original,
                         "patch not restored")


    def test_patch_dict(self):
        foo = {'initial': object(), 'other': 'something'}
        original = foo.copy()

        @patch.dict(foo)
        def test():
            foo['a'] = 3
            del foo['initial']
            foo['other'] = 'something else'

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, {'a': 'b'})
        def test():
            self.assertEqual(len(foo), 3)
            self.assertEqual(foo['a'], 'b')

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, [('a', 'b')])
        def test():
            self.assertEqual(len(foo), 3)
            self.assertEqual(foo['a'], 'b')

        test()

        self.assertEqual(foo, original)


    def test_patch_dict_with_container_object(self):
        foo = Container()
        foo['initial'] = object()
        foo['other'] =  'something'

        original = foo.values.copy()

        @patch.dict(foo)
        def test():
            foo['a'] = 3
            del foo['initial']
            foo['other'] = 'something else'

        test()

        self.assertEqual(foo.values, original)

        @patch.dict(foo, {'a': 'b'})
        def test():
            self.assertEqual(len(foo.values), 3)
            self.assertEqual(foo['a'], 'b')

        test()

        self.assertEqual(foo.values, original)


    def test_patch_dict_with_clear(self):
        foo = {'initial': object(), 'other': 'something'}
        original = foo.copy()

        @patch.dict(foo, clear=True)
        def test():
            self.assertEqual(foo, {})
            foo['a'] = 3
            foo['other'] = 'something else'

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, {'a': 'b'}, clear=True)
        def test():
            self.assertEqual(foo, {'a': 'b'})

        test()

        self.assertEqual(foo, original)

        @patch.dict(foo, [('a', 'b')], clear=True)
        def test():
            self.assertEqual(foo, {'a': 'b'})

        test()

        self.assertEqual(foo, original)


    def test_patch_dict_with_container_object_and_clear(self):
        foo = Container()
        foo['initial'] = object()
        foo['other'] =  'something'

        original = foo.values.copy()

        @patch.dict(foo, clear=True)
        def test():
            self.assertEqual(foo.values, {})
            foo['a'] = 3
            foo['other'] = 'something else'

        test()

        self.assertEqual(foo.values, original)

        @patch.dict(foo, {'a': 'b'}, clear=True)
        def test():
            self.assertEqual(foo.values, {'a': 'b'})

        test()

        self.assertEqual(foo.values, original)


    def test_name_preserved(self):
        foo = {}

        @patch('tests.testpatch.SomeClass', object())
        @patch('tests.testpatch.SomeClass', object(), mocksignature=True)
        @patch.object(SomeClass, object())
        @patch.dict(foo)
        def some_name():
            pass

        self.assertEqual(some_name.__name__, 'some_name')


    def test_patch_with_exception(self):
        foo = {}

        @patch.dict(foo, {'a': 'b'})
        def test():
            raise NameError('Konrad')
        try:
            test()
        except NameError:
            pass
        else:
            self.fail('NameError not raised by test')

        self.assertEqual(foo, {})


    def test_patch_dict_with_string(self):
        @patch.dict('os.environ', {'konrad_delong': 'some value'})
        def test():
            self.assertIn('konrad_delong', os.environ)

        test()


    @unittest2.expectedFailure
    def test_patch_descriptor(self):
        # would be some effort to fix this - we could special case the
        # builtin descriptors: classmethod, property, staticmethod
        class Nothing(object):
            foo = None

        class Something(object):
            foo = {}

            @patch.object(Nothing, 'foo', 2)
            @classmethod
            def klass(cls):
                self.assertIs(cls, Something)

            @patch.object(Nothing, 'foo', 2)
            @staticmethod
            def static(arg):
                return arg

            @patch.dict(foo)
            @classmethod
            def klass_dict(cls):
                self.assertIs(cls, Something)

            @patch.dict(foo)
            @staticmethod
            def static_dict(arg):
                return arg

        # these will raise exceptions if patching descriptors is broken
        self.assertEqual(Something.static('f00'), 'f00')
        Something.klass()
        self.assertEqual(Something.static_dict('f00'), 'f00')
        Something.klass_dict()

        something = Something()
        self.assertEqual(something.static('f00'), 'f00')
        something.klass()
        self.assertEqual(something.static_dict('f00'), 'f00')
        something.klass_dict()


    def test_patch_spec_set(self):
        @patch('tests.testpatch.SomeClass', spec=SomeClass, spec_set=True)
        def test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)

        @patch.object(support, 'SomeClass', spec=SomeClass, spec_set=True)
        def test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)
        @patch('tests.testpatch.SomeClass', spec_set=True)
        def test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)

        @patch.object(support, 'SomeClass', spec_set=True)
        def test(MockClass):
            MockClass.z = 'foo'

        self.assertRaises(AttributeError, test)


    def test_spec_set_inherit(self):
        @patch('tests.testpatch.SomeClass', spec_set=True)
        def test(MockClass):
            instance = MockClass()
            instance.z = 'foo'

        self.assertRaises(AttributeError, test)


    def test_patch_start_stop(self):
        original = something
        patcher = patch('%s.something' % __name__)
        self.assertIs(something, original)
        mock = patcher.start()
        self.assertIsNot(mock, original)
        try:
            self.assertIs(something, mock)
        finally:
            patcher.stop()
        self.assertIs(something, original)


    def test_patchobject_start_stop(self):
        original = something
        patcher = patch.object(PTModule, 'something', 'foo')
        self.assertIs(something, original)
        replaced = patcher.start()
        self.assertEqual(replaced, 'foo')
        try:
            self.assertIs(something, replaced)
        finally:
            patcher.stop()
        self.assertIs(something, original)


    def test_patch_dict_start_stop(self):
        d = {'foo': 'bar'}
        original = d.copy()
        patcher = patch.dict(d, [('spam', 'eggs')], clear=True)
        self.assertEqual(d, original)

        patcher.start()
        self.assertEqual(d, {'spam': 'eggs'})

        patcher.stop()
        self.assertEqual(d, original)


    def test_patch_dict_class_decorator(self):
        this = self
        d = {'spam': 'eggs'}
        original = d.copy()

        class Test(object):
            def test_first(self):
                this.assertEqual(d, {'foo': 'bar'})
            def test_second(self):
                this.assertEqual(d, {'foo': 'bar'})

        Test = patch.dict(d, {'foo': 'bar'}, clear=True)(Test)
        self.assertEqual(d, original)

        test = Test()

        test.test_first()
        self.assertEqual(d, original)

        test.test_second()
        self.assertEqual(d, original)

        test = Test()

        test.test_first()
        self.assertEqual(d, original)

        test.test_second()
        self.assertEqual(d, original)


    def test_get_only_proxy(self):
        class Something(object):
            foo = 'foo'
        class SomethingElse:
            foo = 'foo'

        for thing in Something, SomethingElse, Something(), SomethingElse:
            proxy = _get_proxy(thing)

            @patch.object(proxy, 'foo', 'bar')
            def test():
                self.assertEqual(proxy.foo, 'bar')
            test()
            self.assertEqual(proxy.foo, 'foo')
            self.assertEqual(thing.foo, 'foo')
            self.assertNotIn('foo', proxy.__dict__)


    def test_get_set_delete_proxy(self):
        class Something(object):
            foo = 'foo'
        class SomethingElse:
            foo = 'foo'

        for thing in Something, SomethingElse, Something(), SomethingElse:
            proxy = _get_proxy(Something, get_only=False)

            @patch.object(proxy, 'foo', 'bar')
            def test():
                self.assertEqual(proxy.foo, 'bar')
            test()
            self.assertEqual(proxy.foo, 'foo')
            self.assertEqual(thing.foo, 'foo')
            self.assertNotIn('foo', proxy.__dict__)


    def test_patch_keyword_args(self):
        kwargs = {'side_effect': KeyError, 'foo.bar.return_value': 33,
                  'foo': MagicMock()}

        patcher = patch(foo_name, **kwargs)
        mock = patcher.start()
        patcher.stop()

        self.assertRaises(KeyError, mock)
        self.assertEqual(mock.foo.bar(), 33)
        self.assertIsInstance(mock.foo, MagicMock)


    def test_patch_object_keyword_args(self):
        kwargs = {'side_effect': KeyError, 'foo.bar.return_value': 33,
                  'foo': MagicMock()}

        patcher = patch.object(Foo, 'f', **kwargs)
        mock = patcher.start()
        patcher.stop()

        self.assertRaises(KeyError, mock)
        self.assertEqual(mock.foo.bar(), 33)
        self.assertIsInstance(mock.foo, MagicMock)


    def test_patch_dict_keyword_args(self):
        original = {'foo': 'bar'}
        copy = original.copy()

        patcher = patch.dict(original, foo=3, bar=4, baz=5)
        patcher.start()

        try:
            self.assertEqual(original, dict(foo=3, bar=4, baz=5))
        finally:
            patcher.stop()

        self.assertEqual(original, copy)


    def test_autospec(self):
        class Boo(object):
            def __init__(self, a):
                pass
            def f(self, a):
                pass
            def g(self):
                pass
            foo = 'bar'

            class Bar(object):
                def a(self):
                    pass

        def _test(mock):
            mock(1)
            mock.assert_called_with(1)
            self.assertRaises(TypeError, mock)

        def _test2(mock):
            mock.f(1)
            mock.f.assert_called_with(1)
            self.assertRaises(TypeError, mock.f)

            mock.g()
            mock.g.assert_called_with()
            self.assertRaises(TypeError, mock.g, 1)

            self.assertRaises(AttributeError, getattr, mock, 'h')

            mock.foo.lower()
            mock.foo.lower.assert_called_with()
            self.assertRaises(AttributeError, getattr, mock.foo, 'bar')

            mock.Bar()
            mock.Bar.assert_called_with()

            mock.Bar.a()
            mock.Bar.a.assert_called_with()
            self.assertRaises(TypeError, mock.Bar.a, 1)

            mock.Bar().a()
            mock.Bar().a.assert_called_with()
            self.assertRaises(TypeError, mock.Bar().a, 1)

            self.assertRaises(AttributeError, getattr, mock.Bar, 'b')
            self.assertRaises(AttributeError, getattr, mock.Bar(), 'b')

        def function(mock):
            _test(mock)
            _test2(mock)
            _test2(mock(1))
            self.assertIs(mock, Foo)
            return mock

        test = patch(foo_name, autospec=True)(function)

        mock = test()
        self.assertIsNot(Foo, mock)
        # test patching a second time works
        test()

        module = sys.modules[__name__]
        test = patch.object(module, 'Foo', autospec=True)(function)

        mock = test()
        self.assertIsNot(Foo, mock)
        # test patching a second time works
        test()


    def test_autospec_function(self):
        @patch('%s.function' % __name__, autospec=True)
        def test(mock):
            function(1)
            function.assert_called_with(1)
            function(2, 3)
            function.assert_called_with(2, 3)

            self.assertRaises(TypeError, function)
            self.assertRaises(AttributeError, getattr, function, 'foo')

        test()


    def test_autospec_with_new(self):
        patcher = patch('%s.function' % __name__, new=3, autospec=True)
        self.assertRaises(TypeError, patcher.start)

        module = sys.modules[__name__]
        patcher = patch.object(module, 'function', new=3, autospec=True)
        self.assertRaises(TypeError, patcher.start)


    def test_autospec_with_object(self):
        class Bar(Foo):
            extra = []

        patcher = patch(foo_name, autospec=Bar)
        mock = patcher.start()
        try:
            self.assertIsInstance(mock, Bar)
            self.assertIsInstance(mock.extra, list)
        finally:
            patcher.stop()


    def test_autospec_inherits(self):
        FooClass = Foo
        patcher = patch(foo_name, autospec=True)
        mock = patcher.start()
        try:
            self.assertIsInstance(mock, FooClass)
            self.assertIsInstance(mock(3), FooClass)
        finally:
            patcher.stop()


    def test_autospec_name(self):
        patcher = patch(foo_name, autospec=True)
        mock = patcher.start()
        try:
            self.assertIn("name='Foo'", repr(mock))
            self.assertIn("name='Foo.f'", repr(mock.f))
        finally:
            patcher.stop()


    def test_tracebacks(self):
        @patch.object(Foo, 'f', object())
        def test():
            raise AssertionError
        try:
            test()
        except:
            err = sys.exc_info()

        result = unittest2.TextTestResult(None, None, 0)
        traceback = result._exc_info_to_string(err, self)
        self.assertIn('raise AssertionError', traceback)


    def test_new_callable_patch(self):
        patcher = patch(foo_name, new_callable=NonCallableMagicMock)

        m1 = patcher.start()
        patcher.stop()
        m2 = patcher.start()
        patcher.stop()

        self.assertIsNot(m1, m2)
        for mock in m1, m2:
            self.assertNotCallable(m1)


    def test_new_callable_patch_object(self):
        patcher = patch.object(Foo, 'f', new_callable=NonCallableMagicMock)

        m1 = patcher.start()
        patcher.stop()
        m2 = patcher.start()
        patcher.stop()

        self.assertIsNot(m1, m2)
        for mock in m1, m2:
            self.assertNotCallable(m1)


    def test_new_callable_keyword_arguments(self):
        class Bar(object):
            kwargs = None
            def __init__(self, **kwargs):
                Bar.kwargs = kwargs

        patcher = patch(foo_name, new_callable=Bar, arg1=1, arg2=2)
        m = patcher.start()
        try:
            self.assertIs(type(m), Bar)
            self.assertEqual(Bar.kwargs, dict(arg1=1, arg2=2))
        finally:
            patcher.stop()


    def test_new_callable_spec(self):
        class Bar(object):
            kwargs = None
            def __init__(self, **kwargs):
                Bar.kwargs = kwargs

        patcher = patch(foo_name, new_callable=Bar, spec=Bar)
        m = patcher.start()
        try:
            self.assertEqual(Bar.kwargs, dict(spec=Bar))
        finally:
            patcher.stop()

        patcher = patch(foo_name, new_callable=Bar, spec_set=Bar)
        m = patcher.start()
        try:
            self.assertEqual(Bar.kwargs, dict(spec_set=Bar))
        finally:
            patcher.stop()


    def test_new_callable_create(self):
        non_existent_attr = '%s.weeeee' % foo_name
        p = patch(non_existent_attr, new_callable=NonCallableMock)
        self.assertRaises(AttributeError, p.start)

        p = patch(non_existent_attr, new_callable=NonCallableMock,
                  create=True)
        m = p.start()
        try:
            self.assertNotCallable(m, magic=False)
        finally:
            p.stop()


    def test_new_callable_incompatible_with_new(self):
        self.assertRaises(
            ValueError, patch, foo_name, new=object(), new_callable=MagicMock
        )
        self.assertRaises(
            ValueError, patch.object, Foo, 'f', new=object(),
            new_callable=MagicMock
        )


    def test_new_callable_incompatible_with_autospec(self):
        self.assertRaises(
            ValueError, patch, foo_name, new_callable=MagicMock,
            autospec=True
        )
        self.assertRaises(
            ValueError, patch.object, Foo, 'f', new_callable=MagicMock,
            autospec=True
        )


    def test_new_callable_inherit_for_mocks(self):
        class MockSub(Mock):
            pass

        MockClasses = (
            NonCallableMock, NonCallableMagicMock, MagicMock, Mock, MockSub
        )
        for Klass in MockClasses:
            for arg in 'spec', 'spec_set':
                kwargs = {arg: True}
                p = patch(foo_name, new_callable=Klass, **kwargs)
                m = p.start()
                try:
                    instance = m.return_value
                    self.assertRaises(AttributeError, getattr, instance, 'x')
                finally:
                    p.stop()


    def test_new_callable_inherit_non_mock(self):
        class NotAMock(object):
            def __init__(self, spec):
                self.spec = spec

        p = patch(foo_name, new_callable=NotAMock, spec=True)
        m = p.start()
        try:
            self.assertTrue(is_instance(m, NotAMock))
            self.assertRaises(AttributeError, getattr, m, 'return_value')
        finally:
            p.stop()

        self.assertEqual(m.spec, Foo)


    def test_new_callable_class_decorating(self):
        test = self
        original = Foo
        class SomeTest(object):

            def _test(self, mock_foo):
                test.assertIsNot(Foo, original)
                test.assertIs(Foo, mock_foo)
                test.assertIsInstance(Foo, SomeClass)

            def test_two(self, mock_foo):
                self._test(mock_foo)
            def test_one(self, mock_foo):
                self._test(mock_foo)

        SomeTest = patch(foo_name, new_callable=SomeClass)(SomeTest)
        SomeTest().test_one()
        SomeTest().test_two()
        self.assertIs(Foo, original)


    def test_patch_multiple(self):
        original_foo = Foo
        original_f = Foo.f
        original_g = Foo.g

        patcher1 = patch.multiple(foo_name, f=1, g=2)
        patcher2 = patch.object(Foo, f=1, g=2)

        for patcher in patcher1, patcher2:
            patcher.start()
            try:
                self.assertIs(Foo, original_foo)
                self.assertEqual(Foo.f, 1)
                self.assertEqual(Foo.g, 2)
            finally:
                patcher.stop()

            self.assertIs(Foo, original_foo)
            self.assertEqual(Foo.f, original_f)
            self.assertEqual(Foo.g, original_g)


    def test_patch_multiple_no_kwargs(self):
        self.assertRaises(ValueError, patch.multiple, foo_name)
        self.assertRaises(ValueError, patch.object, Foo)




"""
Test patch.multiple decorating classes
Test patch.multiple mixed with other patchers
Test patch.multiple with patch.start
Test patch.multiple as context manager

A failure on exit of one patcher from a multiple must not prevent the exits
in the rest from running (don't think this can actually happen)

Test patch.multiple with create / spec / spec_set / autospec / mocksignature /
new_callable keyword arguments

With DEFAULT as the value, patch.multiple should create the mock and pass it
into the function as a keyword argument. It should return a dictionary if used
as a context manager (or via patch.start).
"""


if __name__ == '__main__':
    unittest2.main()
