# Copyright (C) 2007-2010 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

from __future__ import with_statement

import os
import sys

info = sys.version_info
if info[:3] >= (3, 2, 0) or info[0] == 2 and info[1] >= 7:
    # for Python 2.7 and 3.2 ordinary unittest is fine
    import unittest as unittest2
else:
    import unittest2

this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not this_dir in sys.path:
    sys.path.insert(0, this_dir)

if __name__ == '__main__':
    sys.modules['testwith'] = sys.modules['__main__']

if 'testwith' in sys.modules:
    # Fix for running tests under Wing
    import tests
    import testwith
    tests.testwith = testwith

from mock import MagicMock, Mock, patch, sentinel

something  = sentinel.Something
something_else  = sentinel.SomethingElse

try:
    from contextlib import nested
except ImportError:
    from contextlib import contextmanager
    @contextmanager
    def nested(*managers):
        exits = []
        vars = []
        exc = (None, None, None)
        try:
            for mgr in managers:
                exit = mgr.__exit__
                enter = mgr.__enter__
                vars.append(enter())
                exits.append(exit)
            yield vars
        except:
            exc = sys.exc_info()
        finally:
            while exits:
                exit = exits.pop()
                try:
                    if exit(*exc):
                        exc = (None, None, None)
                except:
                    exc = sys.exc_info()
            if exc != (None, None, None):
                raise exc[1]


class WithTest(unittest2.TestCase):
    def testWithStatement(self):
        with patch('tests.testwith.something', sentinel.Something2):
            self.assertEqual(something, sentinel.Something2, "unpatched")        
        self.assertEqual(something, sentinel.Something)
        
    def testWithStatementException(self):
        try:
            with patch('tests.testwith.something', sentinel.Something2):
                self.assertEqual(something, sentinel.Something2, "unpatched")   
                raise Exception('pow')
        except Exception:
            pass
        else:
            self.fail("patch swallowed exception")
        self.assertEqual(something, sentinel.Something)


    def testWithStatementAs(self):
        with patch('tests.testwith.something') as mock_something:
            self.assertEqual(something, mock_something, "unpatched")        
            self.assertTrue(isinstance(mock_something, Mock), "patching wrong type")
        self.assertEqual(something, sentinel.Something)


    def testPatchObjectWithStatementAs(self):
        mock = Mock()
        original = mock.something
        with patch.object(mock, 'something'):
            self.assertNotEquals(mock.something, original, "unpatched")        
        self.assertEqual(mock.something, original)


    def testWithStatementNested(self):
        with nested(patch('tests.testwith.something'), 
                    patch('tests.testwith.something_else')) as (mock_something, mock_something_else):
            self.assertEqual(something, mock_something, "unpatched")
            self.assertEqual(something_else, mock_something_else, "unpatched")
        self.assertEqual(something, sentinel.Something)
        self.assertEqual(something_else, sentinel.SomethingElse)


    def testWithStatementSpecified(self):
        with patch('tests.testwith.something', sentinel.Patched) as mock_something:
            self.assertEqual(something, mock_something, "unpatched")        
            self.assertEqual(mock_something, sentinel.Patched, "wrong patch")        
        self.assertEqual(something, sentinel.Something)

    
    def testContextManagerMocking(self):
        mock = Mock()
        mock.__enter__ = Mock()
        mock.__exit__ = Mock()
        mock.__exit__.return_value = False
        
        with mock as m:
            self.assertEqual(m, mock.__enter__.return_value)
        mock.__enter__.assert_called_with()
        mock.__exit__.assert_called_with(None, None, None)

    
    def testContextManagerWithMagicMock(self):
        mock = MagicMock()
        
        with self.assertRaises(TypeError):
            with mock:
                'foo' + 3
        mock.__enter__.assert_called_with()
        self.assertTrue(mock.__exit__.called)


    def testWithStatementSameAttribute(self):
        with patch('tests.testwith.something', sentinel.Patched) as mock_something:
            self.assertEquals(something, mock_something, "unpatched")

            with patch('tests.testwith.something') as mock_again:
                self.assertEquals(something, mock_again, "unpatched")

            self.assertEquals(something, mock_something, "restored with wrong instance")

        self.assertEquals(something, sentinel.Something, "not restored")


if __name__ == '__main__':
    unittest2.main()
    
