# Copyright (C) 2007-2010 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

import os
import sys

info = sys.version_info
if info[:3] >= (3, 2, 0) or info[0] == 2 and info[1] >= 7:
    # for Python 2.7 and 3.2 ordinary unittest is fine
    import unittest as unittest2
else:
    import unittest2

try:
    unicode
except NameError:
    # Python 3
    unicode = str

inPy3k = sys.version_info[0] == 3

this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not this_dir in sys.path:
    # Fix for running tests on the Mac 
    sys.path.insert(0, this_dir)


if 'testmagicmethods' in sys.modules:
    # Fix for running tests under Wing
    import tests
    import testmagicmethods
    tests.testmagicmethods = testmagicmethods

import inspect
from mock import Mock, MagicMock, _all_magics


class TestMockingMagicMethods(unittest2.TestCase):
    
    def testDeletingMagicMethods(self):
        mock = Mock()
        self.assertFalse(hasattr(mock, '__getitem__'))
        
        mock.__getitem__ = Mock()
        self.assertTrue(hasattr(mock, '__getitem__'))
        
        del mock.__getitem__
        self.assertFalse(hasattr(mock, '__getitem__'))
    
    
    def testMagicMethodWrapping(self):
        mock = Mock()
        def f(self, name):
            return self, 'fish'
        
        mock.__getitem__ = f
        self.assertFalse(mock.__getitem__ is f)
        self.assertEqual(mock['foo'], (mock, 'fish'))
        
        # When you pull the function back of the *instance*
        # the first argument (self) is removed
        def instance_f(name):
            pass
        self.assertEqual(inspect.getargspec(mock.__getitem__), inspect.getargspec(instance_f))
        
        mock.__getitem__ = mock
        self.assertTrue(mock.__getitem__ is mock)
        
        
    def testRepr(self):
        mock = Mock()
        self.assertEqual(repr(mock), object.__repr__(mock))
        mock.__repr__ = lambda s: 'foo'
        self.assertEqual(repr(mock), 'foo')


    def testStr(self):
        mock = Mock()
        self.assertEqual(str(mock), object.__str__(mock))
        mock.__str__ = lambda s: 'foo'
        self.assertEqual(str(mock), 'foo')
    
    @unittest2.skipIf(inPy3k, "no unicode in Python 3")
    def testUnicode(self):
        mock = Mock()
        self.assertEquals(unicode(mock), unicode(str(mock)))
        
        mock.__unicode__ = lambda s: unicode('foo')
        self.assertEqual(unicode(mock), unicode('foo'))
    
    
    def testDictMethods(self):
        mock = Mock()
        
        self.assertRaises(TypeError, lambda: mock['foo'])
        def _del():
            del mock['foo']
        def _set():
            mock['foo'] = 3
        self.assertRaises(TypeError, _del)
        self.assertRaises(TypeError, _set)
        
        _dict = {}
        def getitem(s, name):
            return _dict[name]    
        def setitem(s, name, value):
            _dict[name] = value
        def delitem(s, name):
            del _dict[name]
        
        mock.__setitem__ = setitem
        mock.__getitem__ = getitem
        mock.__delitem__ = delitem
        
        self.assertRaises(KeyError, lambda: mock['foo'])
        mock['foo'] = 'bar'
        self.assertEquals(_dict, {'foo': 'bar'})
        self.assertEquals(mock['foo'], 'bar')
        del mock['foo']
        self.assertEquals(_dict, {})
            
            
    def testNumeric(self):
        original = mock = Mock()
        mock.value = 0
        
        self.assertRaises(TypeError, lambda: mock + 3)
        
        def add(self, other):
            mock.value += other
            return self
        mock.__add__ = add
        self.assertEqual(mock + 3, mock)
        self.assertEqual(mock.value, 3)
        
        del mock.__add__
        def iadd(mock):
            mock += 3
        self.assertRaises(TypeError, iadd, mock)
        mock.__iadd__ = add
        mock += 6
        self.assertEqual(mock, original)
        self.assertEqual(mock.value, 9)
        
        self.assertRaises(TypeError, lambda: 3 + mock)
        mock.__radd__ = add
        self.assertEqual(7 + mock, mock)
        self.assertEqual(mock.value, 16)
    
    
    def testHash(self):
        mock = Mock()
        # test delegation
        self.assertEqual(hash(mock), Mock.__hash__(mock))
        
        def _hash(s):
            return 3
        mock.__hash__ = _hash
        self.assertEqual(hash(mock), 3)
    
    
    def testNonZero(self):
        m = Mock()
        self.assertTrue(bool(m))
        
        nonzero = lambda s: False
        m.__nonzero__ = nonzero
        
        # Needed for Python 3
        m.__bool__ = nonzero
        
        self.assertFalse(bool(m))
    
        
    def testComparison(self):
        if not inPy3k:
            # incomparable in Python 3
            self. assertEqual(Mock() < 3, object() < 3)
            self. assertEqual(Mock() > 3, object() > 3)
            self. assertEqual(Mock() <= 3, object() <= 3)
            self. assertEqual(Mock() >= 3, object() >= 3)
        
        mock = Mock()
        def comp(s, o):
            return True
        mock.__lt__ = mock.__gt__ = mock.__le__ = mock.__ge__ = comp
        self. assertTrue(mock < 3)
        self. assertTrue(mock > 3)
        self. assertTrue(mock <= 3)
        self. assertTrue(mock >= 3)

    
    def testEquality(self):
        mock = Mock()
        self.assertEqual(mock, mock)
        self.assertNotEqual(mock, Mock())
        self.assertNotEqual(mock, 3)
        
        def eq(self, other):
            return other == 3
        mock.__eq__ = eq
        self.assertTrue(mock == 3)
        self.assertFalse(mock == 4)
        
        def ne(self, other):
            return other == 3
        mock.__ne__ = ne
        self.assertTrue(mock != 3)
        self.assertFalse(mock != 4)
    
    
    def testLenContainsIter(self):
        mock = Mock()
        
        self.assertRaises(TypeError, len, mock)
        self.assertRaises(TypeError, iter, mock)
        self.assertRaises(TypeError, lambda: 'foo' in mock)
        
        mock.__len__ = lambda s: 6
        self.assertEqual(len(mock), 6)
        
        mock.__contains__ = lambda s, o: o == 3
        self.assertTrue(3 in mock)
        self.assertFalse(6 in mock)
        
        mock.__iter__ = lambda s: iter('foobarbaz')
        self.assertEqual(list(mock), list('foobarbaz'))


    def testMagicMock(self):
        mock = MagicMock()
        
        mock.__iter__.return_value = iter([1, 2, 3])
        self.assertEqual(list(mock), [1, 2, 3])
        
        if inPy3k:
            mock.__bool__.return_value = False
        else:
            mock.__nonzero__.return_value = False
            # in Python 3 mock still has a __nonzero__ attribute
            self.assertFalse(hasattr(mock, '__bool__'))
        
        self.assertFalse(bool(mock))
        
        for entry in _all_magics:
            self.assertTrue(hasattr(mock, entry))
        self.assertFalse(hasattr(mock, '__imaginery__'))

if __name__ == '__main__':
    unittest2.main()
    
