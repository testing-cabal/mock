# Tests to make sure helpers we backport are actually working!
from unittest import TestCase

from .support import uncache


class TestUncache(TestCase):

    def test_cant_uncache_sys(self):
        with self.assertRaises(ValueError):
            with uncache('sys'): pass

    def test_uncache_non_existent(self):
        with uncache('mock.tests.support.bad'): pass
