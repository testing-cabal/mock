# Copyright (C) 2007-2011 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

from tests.support import is_instance, unittest2, X, SomeClass

from mock import (
    Mock, MagicMock, NonCallableMagicMock,
    NonCallableMock, patch, create_autospec
)

"""
Note that NonCallableMock and NonCallableMagicMock still have the unused (and
unusable) attributes: return_value, side_effect, call_count, call_args and
call_args_list. These could be removed or raise errors on getting / setting.

They also have the assert_called_with and assert_called_once_with methods.
Removing these would be pointless as fetching them would create a mock
(attribute) that could be called without error.
"""


class TestCallable(unittest2.TestCase):

    def test_non_callable(self):
        for mock in NonCallableMagicMock(), NonCallableMock():
            self.assertRaises(TypeError, mock)
            self.assertFalse(hasattr(mock, '__call__'))


    def test_attributes(self):
        one = NonCallableMock()
        self.assertTrue(issubclass(type(one.one), Mock))

        two = NonCallableMagicMock()
        self.assertTrue(issubclass(type(two.two), MagicMock))


    def test_subclasses(self):
        class MockSub(Mock):
            pass

        one = MockSub()
        self.assertTrue(issubclass(type(one.one), MockSub))

        class MagicSub(MagicMock):
            pass

        two = MagicSub()
        self.assertTrue(issubclass(type(two.two), MagicSub))


    def test_patch_spec(self):
        patcher = patch('%s.X' % __name__, spec=True)
        mock = patcher.start()
        self.addCleanup(patcher.stop)

        instance = mock()
        mock.assert_called_once_with()

        self.assertTrue(is_instance(instance, NonCallableMagicMock))
        self.assertRaises(TypeError, instance)


    def test_patch_spec_instance(self):
        patcher = patch('%s.X' % __name__, spec=X())
        mock = patcher.start()
        self.addCleanup(patcher.stop)

        self.assertTrue(is_instance(mock, NonCallableMagicMock))
        self.assertRaises(TypeError, mock)


    def test_patch_spec_callable_class(self):
        class CallableX(X):
            def __call__(self):
                pass

        class Sub(CallableX):
            pass

        class Multi(SomeClass, Sub):
            pass

        class OldStyle:
            def __call__(self):
                pass

        class OldStyleSub(OldStyle):
            pass

        for Klass in CallableX, Sub, Multi, OldStyle, OldStyleSub:
            patcher = patch('%s.X' % __name__, spec=Klass)
            mock = patcher.start()
            self.addCleanup(patcher.stop)

            instance = mock()
            mock.assert_called_once_with()

            self.assertTrue(is_instance(instance, MagicMock))
            instance()
            instance.assert_called_once_with()


    def test_create_autopsec(self):
        mock = create_autospec(X)
        instance = mock()
        self.assertRaises(TypeError, instance)

        mock = create_autospec(X())
        self.assertRaises(TypeError, mock)

