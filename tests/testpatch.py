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
    from warnings import catch_warnings
except ImportError:
    catch_warnings = None


this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if this_dir not in sys.path:
    # Fix for running tests on the Mac 
    sys.path.insert(0, this_dir)
    
if __name__ == '__main__':
    sys.modules['testpatch'] = sys.modules['__main__']
    
if 'testpatch' in sys.modules:
    # Fix for running tests under Wing
    import tests
    import testpatch
    tests.testpatch = testpatch

from mock import Mock, patch, patch_object, sentinel

builtin_string = '__builtin__'
try:
    apply
except NameError:
    # no apply in Python 3
    def apply(f, *args, **kw):
        f(*args, **kw)
    builtin_string = 'builtins'


# for use in the test
something  = sentinel.Something
something_else  = sentinel.SomethingElse


class SomeClass(object):
    class_attribute = None
    
    def wibble(self):
        pass

    
class PatchTest(unittest2.TestCase):

    def testSinglePatchObject(self):
        class Something(object):
            attribute = sentinel.Original
          
        @apply
        @patch.object(Something, 'attribute', sentinel.Patched)
        def test():
            self.assertEqual(Something.attribute, sentinel.Patched, "unpatched")
            
        self.assertEqual(Something.attribute, sentinel.Original, "patch not restored")

        
    def testPatchObjectWithNone(self):
        class Something(object):
            attribute = sentinel.Original
          
        @apply
        @patch.object(Something, 'attribute', None)
        def test():
            self.assertIsNone(Something.attribute, "unpatched")
            
        self.assertEqual(Something.attribute, sentinel.Original, "patch not restored")
        

    def testMultiplePatchObject(self):
        class Something(object):
            attribute = sentinel.Original
            next_attribute = sentinel.Original2
        
        @apply
        @patch.object(Something, 'attribute', sentinel.Patched)
        @patch.object(Something, 'next_attribute', sentinel.Patched2)
        def test():
            self.assertEqual(Something.attribute, sentinel.Patched, "unpatched")
            self.assertEqual(Something.next_attribute, sentinel.Patched2, "unpatched")
            
        self.assertEqual(Something.attribute, sentinel.Original, "patch not restored")
        self.assertEqual(Something.next_attribute, sentinel.Original2, "patch not restored")


    def testObjectLookupIsQuiteLazy(self):
        global something
        original = something
        @patch('tests.testpatch.something', sentinel.Something2)
        def test():
            pass
        
        try:
            something = sentinel.replacement_value
            test()
            self.assertEqual(something, sentinel.replacement_value)
        finally:
            something = original


    def testPatch(self):
        import __main__
        __main__.something = sentinel.Something
        
        @apply
        @patch('__main__.something', sentinel.Something2)
        def test():
            self.assertEqual(__main__.something, sentinel.Something2, "unpatched")
            
        self.assertEqual(__main__.something, sentinel.Something, "patch not restored")
                
        import tests.testpatch as PTModule
        
        @patch('tests.testpatch.something', sentinel.Something2)
        @patch('tests.testpatch.something_else', sentinel.SomethingElse)
        def test():
            self.assertEqual(PTModule.something, sentinel.Something2, "unpatched")
            self.assertEqual(PTModule.something_else, sentinel.SomethingElse, "unpatched")
        
        self.assertEqual(PTModule.something, sentinel.Something, "patch not restored")
        self.assertEqual(PTModule.something_else, sentinel.SomethingElse, "patch not restored")
        
        # Test the patching and restoring works a second time
        test()   
            
        self.assertEqual(PTModule.something, sentinel.Something, "patch not restored")
        self.assertEqual(PTModule.something_else, sentinel.SomethingElse, "patch not restored")
        
        mock = Mock()
        mock.return_value = sentinel.Handle
        @patch('%s.open' % builtin_string, mock)
        def test():
            self.assertEqual(open('filename', 'r'), sentinel.Handle, "open not patched")
        test()
        test()
        
        self.assertNotEquals(open, mock, "patch not restored")

        
    def testPatchClassAttribute(self):
        import tests.testpatch as PTModule

        @patch('tests.testpatch.SomeClass.class_attribute', sentinel.ClassAttribute)
        def test():
            self.assertEqual(PTModule.SomeClass.class_attribute, sentinel.ClassAttribute, "unpatched")
        test()   
        
        self.assertIsNone(PTModule.SomeClass.class_attribute, "patch not restored")
        

    def testPatchObjectWithDefaultMock(self):
        class Test(object):
            something = sentinel.Original
            something2 = sentinel.Original2
        
        @apply
        @patch.object(Test, 'something')
        def test(mock):
            self.assertEqual(mock, Test.something, "Mock not passed into test function")
            self.assertTrue(isinstance(mock, Mock), 
                            "patch with two arguments did not create a mock")
                            
        @patch.object(Test, 'something')                    
        @patch.object(Test, 'something2')
        def test(this1, this2, mock1, mock2):
            self.assertEqual(this1, sentinel.this1, "Patched function didn't receive initial argument")
            self.assertEqual(this2, sentinel.this2, "Patched function didn't receive second argument")
            self.assertEqual(mock1, Test.something2, "Mock not passed into test function")
            self.assertEqual(mock2, Test.something, "Second Mock not passed into test function")
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
        @patch('tests.testpatch.SomeClass', spec=SomeClass)
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertTrue(isinstance(SomeClass.wibble, Mock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)
            
        test()

        
    def testPatchObjectWithSpec(self):
        @patch.object(SomeClass, 'class_attribute', spec=SomeClass)
        def test(MockAttribute):
            self.assertEqual(SomeClass.class_attribute, MockAttribute)
            self.assertTrue(isinstance(SomeClass.class_attribute.wibble, Mock))
            self.assertRaises(AttributeError, lambda: SomeClass.class_attribute.not_wibble)
            
        test()

        
    def testPatchWithSpecAsList(self):
        @patch('tests.testpatch.SomeClass', spec=['wibble'])
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertTrue(isinstance(SomeClass.wibble, Mock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)
            
        test()

        
    def testPatchObjectWithSpecAsList(self):
        @patch.object(SomeClass, 'class_attribute', spec=['wibble'])
        def test(MockAttribute):
            self.assertEqual(SomeClass.class_attribute, MockAttribute)
            self.assertTrue(isinstance(SomeClass.class_attribute.wibble, Mock))
            self.assertRaises(AttributeError, lambda: SomeClass.class_attribute.not_wibble)
            
        test()
        
    
    def testNestedPatchWithSpecAsList(self):
        # regression test for nested decorators
        @patch('%s.open' % builtin_string)
        @patch('tests.testpatch.SomeClass', spec=['wibble'])
        def test(MockSomeClass, MockOpen):
            self.assertEqual(SomeClass, MockSomeClass)
            self.assertTrue(isinstance(SomeClass.wibble, Mock))
            self.assertRaises(AttributeError, lambda: SomeClass.not_wibble)
        
        
    def testPatchWithSpecAsBoolean(self):
        @apply
        @patch('tests.testpatch.SomeClass', spec=True)
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            # Should not raise attribute error
            MockSomeClass.wibble
            
            self.assertRaises(AttributeError, lambda: MockSomeClass.not_wibble)
      
        
    def testPatchObjectWithSpecAsBoolean(self):
        from tests import testpatch
        @apply
        @patch.object(testpatch, 'SomeClass', spec=True)
        def test(MockSomeClass):
            self.assertEqual(SomeClass, MockSomeClass)
            # Should not raise attribute error
            MockSomeClass.wibble
            
            self.assertRaises(AttributeError, lambda: MockSomeClass.not_wibble)
        
    
    def testPatchClassActsWithSpecIsInherited(self):
        @apply
        @patch('tests.testpatch.SomeClass', spec=True)
        def test(MockSomeClass):
            instance = MockSomeClass()
            # Should not raise attribute error
            instance.wibble
            
            self.assertRaises(AttributeError, lambda: instance.not_wibble)
        
        
    def testPatchWithCreateMocksNonExistentAttributes(self):
        @patch('%s.frooble' % builtin_string, sentinel.Frooble, create=True)
        def test():
            self.assertEqual(frooble, sentinel.Frooble)
            
        test()
        self.assertRaises(NameError, lambda: frooble)
        
        
    def testPatchObjectWithCreateMocksNonExistentAttributes(self):
        @patch.object(SomeClass, 'frooble', sentinel.Frooble, create=True)
        def test():
            self.assertEqual(SomeClass.frooble, sentinel.Frooble)
            
        test()
        self.assertFalse(hasattr(SomeClass, 'frooble'))
        
        
    def testPatchWontCreateByDefault(self):
        try:
            @patch('%s.frooble' % builtin_string, sentinel.Frooble)
            def test():
                self.assertEqual(frooble, sentinel.Frooble)
                
            test()
        except AttributeError:
            pass
        else:
            self.fail('Patching non existent attributes should fail')
            
        self.assertRaises(NameError, lambda: frooble)
        
        
    def testPatchObjecWontCreateByDefault(self):
        try:
            @patch.object(SomeClass, 'frooble', sentinel.Frooble)
            def test():
                self.assertEqual(SomeClass.frooble, sentinel.Frooble)
                
            test()
        except AttributeError:
            pass
        else:
            self.fail('Patching non existent attributes should fail')
        self.assertFalse(hasattr(SomeClass, 'frooble'))
        
        
    def testPathWithStaticMethods(self):
        class Foo(object):
            @staticmethod
            def woot():
                return sentinel.Static
        
        @patch.object(Foo, 'woot', staticmethod(lambda: sentinel.Patched))
        def anonymous():
            self.assertEqual(Foo.woot(), sentinel.Patched)
        anonymous()
        
        self.assertEqual(Foo.woot(), sentinel.Static)
        
        
    def testPatchLocal(self):
        foo = sentinel.Foo
        @patch.object(sentinel, 'Foo', 'Foo')
        def anonymous():
            self.assertEqual(sentinel.Foo, 'Foo')
        anonymous()
        
        self.assertEqual(sentinel.Foo, foo)


    def testPatchSlots(self):
        class Foo(object):
            __slots__ = ('Foo',)
        
        foo = Foo()
        foo.Foo = sentinel.Foo
        
        @patch.object(foo, 'Foo', 'Foo')
        def anonymous():
            self.assertEqual(foo.Foo, 'Foo')
        anonymous()
        
        self.assertEqual(foo.Foo, sentinel.Foo)

    def testPatchObjectClassDecorator(self):
        class Something(object):
            attribute = sentinel.Original

        class Foo(object):
            def test_method(other_self):
                self.assertEqual(Something.attribute, sentinel.Patched, "unpatched")
            def not_test_method(other_self):
                self.assertEqual(Something.attribute, sentinel.Original, "non-test method patched")
        Foo = patch.object(Something, 'attribute', sentinel.Patched)(Foo)

        f = Foo()
        f.test_method()
        f.not_test_method()

        self.assertEqual(Something.attribute, sentinel.Original, "patch not restored")


    def testPatchClassDecorator(self):
        import __main__
        __main__.something = sentinel.Something

        class Something(object):
            attribute = sentinel.Original

        class Foo(object):
            def test_method(other_self, mock_something):
                self.assertEqual(__main__.something, mock_something, "unpatched")
            def not_test_method(other_self):
                self.assertEqual(__main__.something, sentinel.Something, "non-test method patched")
        Foo = patch('__main__.something')(Foo)

        f = Foo()
        f.test_method()
        f.not_test_method()

        self.assertEqual(Something.attribute, sentinel.Original, "patch not restored")
        self.assertEqual(__main__.something, sentinel.Something, "patch not restored")

    @unittest2.skipIf(catch_warnings is None, "test requires catch_warnings decorator")
    def testPatchObjectDeprecation(self):
        with catch_warnings(record=True) as ws:
            patch_object(SomeClass, 'class_attribute', spec=SomeClass)
            warning = ws[0]
            self.assertIs(warning.category, DeprecationWarning)


if __name__ == '__main__':
    unittest2.main()
    
