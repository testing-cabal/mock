# Copyright (C) 2007-2011 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

from tests.support import unittest2

from mock import Mock, MagicMock, NonCallableMagicMock, NonCallableMock


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

