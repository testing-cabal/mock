# Copyright (C) 2007-2010 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

import inspect

from tests.support import unittest2, apply

from mock import Mock, mocksignature, patch



class TestMockSignature(unittest2.TestCase):

    def testFunction(self):
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
        
    def testFunctionWithoutExplicitMock(self):
        def f(a):
            pass
        
        f2  = mocksignature(f)
        self.assertIsInstance(f2.mock, Mock)
        
        self.assertRaises(TypeError, f2)
        f2.mock.return_value = 3
        self.assertEqual(f2('foo'), 3)
        f2.mock.assert_called_with('foo')
    
    
    def testMethod(self):
        class Foo(object):
            def method(self, a, b):
                pass
        
        f = Foo()
        mock = Mock()
        mock.return_value = 3
        f.method = mocksignature(f.method, mock)
        self.assertEqual(f.method('foo', 'bar'), 3)
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
    
    
    def testMockSignatureWithPatch(self):
        mock = Mock()
        
        def f(a, b, c):
            pass
        mock.f = f
        
        @apply
        @patch.object(mock, 'f', mocksignature=True)
        def test(mock_f):
            self.assertRaises(TypeError, mock.f, 3, 4)
            self.assertRaises(TypeError, mock.f, 3, 4, 5, 6)
            mock.f(1, 2, 3)
            
            mock_f.assert_called_with(1, 2, 3)
            mock.f.mock.assert_called_with(1, 2, 3)
        
        @apply
        @patch('tests.support.SomeClass.wibble', mocksignature=True)
        def test(mock_wibble):
            from tests.support import SomeClass
            
            instance = SomeClass()
            self.assertRaises(TypeError, instance.wibble, 1)
            instance.wibble()
            
            mock_wibble.assert_called_with(instance)
            instance.wibble.mock.assert_called_with(instance)
