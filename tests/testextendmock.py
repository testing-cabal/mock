# Copyright (C) 2007-20010 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

import os
import sys
import unittest
this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not this_dir in sys.path:
    # Fix for running tests on the Mac 
    sys.path.insert(0, this_dir)


if 'testextendmock' in sys.modules:
    # Fix for running tests under Wing
    import tests
    import testextendmock
    tests.testextendmock = testextendmock

from testcase import TestCase

from mock import Mock
from extendmock import mocksignature, MagicMock


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
        
        

if __name__ == '__main__':
    unittest.main()
    
