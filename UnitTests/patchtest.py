# Copyright (C) 2007-2008 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock.html

import os
import sys
this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not this_dir in sys.path:
    sys.path.insert(0, this_dir)

from testcase import TestCase
from testutils import RunTests

from mock import Mock, patch, patch_object, sentinel


# for use in the test
something  = sentinel.Something
something_else  = sentinel.SomethingElse

class SomeClass(object):
    class_attribute = None


class PatchTest(TestCase):

    def testSinglePatchObject(self):
        class Something(object):
            attribute = sentinel.Original
          
        @apply
        @patch_object(Something, 'attribute', sentinel.Patched)
        def test():
            self.assertEquals(Something.attribute, sentinel.Patched, "unpatched")
            
        self.assertEquals(Something.attribute, sentinel.Original, "patch not restored")

        
    def testPatchObjectWithNone(self):
        class Something(object):
            attribute = sentinel.Original
          
        @apply
        @patch_object(Something, 'attribute', None)
        def test():
            self.assertNone(Something.attribute, "unpatched")
            
        self.assertEquals(Something.attribute, sentinel.Original, "patch not restored")
        

    def testMultiplePatchObject(self):
        class Something(object):
            attribute = sentinel.Original
            next_attribute = sentinel.Original2
        
        @apply
        @patch_object(Something, 'attribute', sentinel.Patched)
        @patch_object(Something, 'next_attribute', sentinel.Patched2)
        def test():
            self.assertEquals(Something.attribute, sentinel.Patched, "unpatched")
            self.assertEquals(Something.next_attribute, sentinel.Patched2, "unpatched")
            
        self.assertEquals(Something.attribute, sentinel.Original, "patch not restored")
        self.assertEquals(Something.next_attribute, sentinel.Original2, "patch not restored")


    def testPatch(self):
        import __main__
        __main__.something = sentinel.Something
        
        @apply
        @patch('__main__.something', sentinel.Something2)
        def test():
            self.assertEquals(__main__.something, sentinel.Something2, "unpatched")
            
        self.assertEquals(__main__.something, sentinel.Something, "patch not restored")
                
        import UnitTests.patchtest as PTModule
        
        @patch('UnitTests.patchtest.something', sentinel.Something2)
        @patch('UnitTests.patchtest.something_else', sentinel.SomethingElse)
        def test():
            self.assertEquals(PTModule.something, sentinel.Something2, "unpatched")
            self.assertEquals(PTModule.something_else, sentinel.SomethingElse, "unpatched")
        test()   
        
        self.assertEquals(PTModule.something, sentinel.Something, "patch not restored")
        self.assertEquals(PTModule.something_else, sentinel.SomethingElse, "patch not restored")
        
        # Test the patching and restoring works a second time
        test()   
            
        self.assertEquals(PTModule.something, sentinel.Something, "patch not restored")
        self.assertEquals(PTModule.something_else, sentinel.SomethingElse, "patch not restored")
        
        mock = Mock()
        mock.return_value = sentinel.Handle
        @patch('__builtin__.open', mock)
        def test():
            self.assertEquals(open('filename', 'r'), sentinel.Handle, "open not patched")
        test()
        test()
        
        self.assertNotEquals(open, mock, "patch not restored")

        
    def testPatchClassAttribute(self):
        import UnitTests.patchtest as PTModule

        @patch('UnitTests.patchtest.SomeClass.class_attribute', sentinel.ClassAttribute)
        def test():
            self.assertEquals(PTModule.SomeClass.class_attribute, sentinel.ClassAttribute, "unpatched")
        test()   
        
        self.assertNone(PTModule.SomeClass.class_attribute, "patch not restored")
        

    def testPatchObjectWithDefaultMock(self):
        class Test(object):
            something = sentinel.Original
            something2 = sentinel.Original2
        
        @apply
        @patch_object(Test, 'something')
        def test(mock):
            self.assertEquals(mock, Test.something, "Mock not passed into test function")
            self.assertTrue(isinstance(mock, Mock), 
                            "patch with two arguments did not create a mock")
                            
        @patch_object(Test, 'something')                    
        @patch_object(Test, 'something2')
        def test(this1, this2, mock1, mock2):
            self.assertEquals(this1, sentinel.this1, "Patched function didn't receive initial argument")
            self.assertEquals(this2, sentinel.this2, "Patched function didn't receive second argument")
            self.assertEquals(mock1, Test.something, "Mock not passed into test function")
            self.assertEquals(mock2, Test.something2, "Second Mock not passed into test function")
            self.assertTrue(isinstance(mock2, Mock), 
                            "patch with two arguments did not create a mock")
            self.assertTrue(isinstance(mock2, Mock), 
                            "patch with two arguments did not create a mock")
                            
            
            # A hack to test that new mocks are passed the second time
            self.assertNotEquals(outerMock1, mock1, "unexpected value for mock1")                
            self.assertNotEquals(outerMock2, mock2, "unexpected value for mock1")
            return mock1, mock2

        outerMock1 = None
        outerMock2 = None
        outerMock1, outerMock2 = test(sentinel.this1, sentinel.this2)
        
        # Test that executing a second time creates new mocks
        test(sentinel.this1, sentinel.this2)


if __name__ == '__main__':
    RunTests(PatchTest)
