# Copyright (C) 2007-2010 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

import os
import sys
import unittest2
this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not this_dir in sys.path:
    # Fix for running tests on the Mac 
    sys.path.insert(0, this_dir)


if 'testmocksignature' in sys.modules:
    # Fix for running tests under Wing
    import tests
    import testmocksignature
    tests.testmocksignature = testmocksignature

from testcase import TestCase

import inspect
from mock import Mock, mocksignature


class TestMockSignature(TestCase):

    def testFunction(self):
        def f(a):
            pass
        mock = Mock()
        
        f2  = mocksignature(f, mock)
        self.assertRaises(TypeError, f2)
        mock.return_value = 3
        self.assertEquals(f2('foo'), 3)
        mock.assert_called_with('foo')
    
    
    def testMethod(self):
        class Foo(object):
            def method(self, a, b):
                pass
        
        f = Foo()
        mock = Mock()
        mock.return_value = 3
        f.method = mocksignature(f.method, mock)
        self.assertEquals(f.method('foo', 'bar'), 3)
        mock.assert_called_with('foo', 'bar')


    def testFunctionWithDefaults(self):
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
        
    def testIntrospection(self):
        def f(a, *args, **kwargs):
            pass
        f2 = mocksignature(f, f)
        self.assertEqual(inspect.getargspec(f), inspect.getargspec(f2))
        
        def f(a, b=None, c=3, d=object()):
            pass
        f2 = mocksignature(f, f)
        self.assertEqual(inspect.getargspec(f), inspect.getargspec(f2))
    
    
    def testFunctionWithVarArgsAndKwargs(self):
        def f(a, b=None, *args, **kwargs):
            return (a, b, args, kwargs)
        f2 = mocksignature(f, f)
        self.assertEqual(f2(3, 4, 5, x=6, y=9), (3, 4, (5,), {'x': 6, 'y': 9}))
        self.assertEqual(f2(3, x=6, y=9, b='a'), (3, 'a', (), {'x': 6, 'y': 9}))
