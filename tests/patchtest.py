# Copyright (C) 2007-2009 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/



import os
import sys
this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if this_dir not in sys.path:
    # Fix for running tests on the Mac 
    sys.path.insert(0, this_dir)
    
if __name__ == '__main__':
    sys.modules['patchtest'] = sys.modules['__main__']
    
if 'patchtest' in sys.modules:
    # Fix for running tests under Wing
    import tests
    import patchtest
    tests.patchtest = patchtest
    
from testcase import TestCase
from testutils import RunTests

from mock import Mock, patch, patch_object, sentinel


# for use in the test
something  = sentinel.Something
something_else  = sentinel.SomethingElse


class SomeClass(object):
    class_attribute = None
    
    def wibble(self):
        pass

    
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


    def testObjectLookupIsQuiteLazy(self):
        global something
        original = something
        @patch('tests.patchtest.something', sentinel.Something2)
        def test():
            pass
        
        try:
            something = sentinel.replacement_value
            test()
            self.assertEquals(something, sentinel.replacement_value)
        finally:
            something = original
        


    def testPatch(self):
        import __main__
        __main__.something = sentinel.Something
        
        @apply
        @patch('__main__.something', sentinel.Something2)
        def test():
            self.assertEquals(__main__.something, sentinel.Something2, "unpatched")
            
        self.assertEquals(__main__.something, sentinel.Something, "patch not restored")
                
        import tests.patchtest as PTModule
        
        @patch('tests.patchtest.something', sentinel.Something2)
        @patch('tests.patchtest.something_else', sentinel.SomethingElse)
        def test():
            self.assertEquals(PTModule.something, sentinel.Something2, "unpatched")
            self.assertEquals(PTModule.something_else, sentinel.SomethingElse, "unpatched")
        
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
        import tests.patchtest as PTModule

        @patch('tests.patchtest.SomeClass.class_attribute', sentinel.ClassAttribute)
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
            self.assertEquals(mock1, Test.something2, "Mock not passed into test function")
            self.assertEquals(mock2, Test.something, "Second Mock not passed into test function")
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

        
    def testPatchWithSpec(self):
        @patch('tests.patchtest.SomeClass', spec=SomeClass)
        def test(MockSomeClass):
            self.assertEquals(SomeClass, MockSomeClass)
            self.assertTrue(isinstance(SomeClass.wibble, Mock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)
            
        test()

        
    def testPatchObjectWithSpec(self):
        @patch_object(SomeClass, 'class_attribute', spec=SomeClass)
        def test(MockAttribute):
            self.assertEquals(SomeClass.class_attribute, MockAttribute)
            self.assertTrue(isinstance(SomeClass.class_attribute.wibble, Mock))
            self.assertRaises(AttributeError, lambda: SomeClass.class_attribute.not_wibble)
            
        test()

        
    def testPatchWithSpecAsList(self):
        @patch('tests.patchtest.SomeClass', spec=['wibble'])
        def test(MockSomeClass):
            self.assertEquals(SomeClass, MockSomeClass)
            self.assertTrue(isinstance(SomeClass.wibble, Mock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)
            
        test()

        
    def testPatchObjectWithSpecAsList(self):
        @patch_object(SomeClass, 'class_attribute', spec=['wibble'])
        def test(MockAttribute):
            self.assertEquals(SomeClass.class_attribute, MockAttribute)
            self.assertTrue(isinstance(SomeClass.class_attribute.wibble, Mock))
            self.assertRaises(AttributeError, lambda: SomeClass.class_attribute.not_wibble)
            
        test()
        
    
    def testNestedPatchWithSpecAsList(self):
        # regression test for nested decorators
        @patch('__builtin__.open')
        @patch('tests.patchtest.SomeClass', spec=['wibble'])
        def test(MockSomeClass, MockOpen):
            self.assertEquals(SomeClass, MockSomeClass)
            self.assertTrue(isinstance(SomeClass.wibble, Mock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)
        
        
    def testPatchWithSpecAsBoolean(self):
        @apply
        @patch('tests.patchtest.SomeClass', spec=True)
        def test(MockSomeClass):
            self.assertEquals(SomeClass, MockSomeClass)
            # Should not raise attribute error
            MockSomeClass.wibble
            
            self.assertRaises(AttributeError, lambda: MockSomeClass.not_wibble)
      
        
    def testPatchObjectWithSpecAsBoolean(self):
        from tests import patchtest
        @apply
        @patch_object(patchtest, 'SomeClass', spec=True)
        def test(MockSomeClass):
            self.assertEquals(SomeClass, MockSomeClass)
            # Should not raise attribute error
            MockSomeClass.wibble
            
            self.assertRaises(AttributeError, lambda: MockSomeClass.not_wibble)
        
    
    def testPatchClassActsWithSpecIsInherited(self):
        @apply
        @patch('tests.patchtest.SomeClass', spec=True)
        def test(MockSomeClass):
            instance = MockSomeClass()
            # Should not raise attribute error
            instance.wibble
            
            self.assertRaises(AttributeError, lambda: instance.not_wibble)
        
        
    def testPatchWithCreateMocksNonExistentAttributes(self):
        @patch('__builtin__.frooble', sentinel.Frooble, create=True)
        def test():
            self.assertEquals(frooble, sentinel.Frooble)
            
        test()
        self.assertRaises(NameError, lambda: frooble)
        
        
    def testPatchObjectWithCreateMocksNonExistentAttributes(self):
        @patch_object(SomeClass, 'frooble', sentinel.Frooble, create=True)
        def test():
            self.assertEquals(SomeClass.frooble, sentinel.Frooble)
            
        test()
        self.assertFalse(hasattr(SomeClass, 'frooble'))
        
        
    def testPatchWontCreateByDefault(self):
        try:
            @patch('__builtin__.frooble', sentinel.Frooble)
            def test():
                self.assertEquals(frooble, sentinel.Frooble)
                
            test()
        except AttributeError:
            pass
        else:
            self.fail('Patching non existent attributes should fail')
            
        self.assertRaises(NameError, lambda: frooble)
        
        
    def testPatchObjecWontCreateByDefault(self):
        try:
            @patch_object(SomeClass, 'frooble', sentinel.Frooble)
            def test():
                self.assertEquals(SomeClass.frooble, sentinel.Frooble)
                
            test()
        except AttributeError:
            pass
        else:
            self.fail('Patching non existent attributes should fail')
        self.assertFalse(hasattr(SomeClass, 'frooble'))



if __name__ == '__main__':
    RunTests(PatchTest)
