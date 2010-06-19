# Copyright (C) 2007-2010 Michael Foord & the mock team
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

from tests.support import unittest2

from mock import Mock, sentinel, DEFAULT

try:
    unicode
except NameError:
    unicode = str


class MockTest(unittest2.TestCase):

    def testAll(self):
        # if __all__ is badly defined then import * will raise an error
        # We have to exec it because you can't import * inside a method
        # in Python 3
        exec("from mock import *")
        
    def testConstructor(self):
        mock = Mock()
        
        self.assertFalse(mock.called, "called not initialised correctly")
        self.assertEqual(mock.call_count, 0, "call_count not initialised correctly")
        self.assertTrue(isinstance(mock.return_value, Mock), "return_value not initialised correctly")
        
        self.assertEqual(mock.call_args, None, "call_args not initialised correctly")
        self.assertEqual(mock.call_args_list, [], "call_args_list not initialised correctly")
        self.assertEqual(mock.method_calls, [], 
                          "method_calls not initialised correctly")
        
        # Can't use hasattr for this test as it always returns True on a mock...
        self.assertFalse('_items' in mock.__dict__, "default mock should not have '_items' attribute")
        
        self.assertIsNone(mock._parent, "parent not initialised correctly")
        self.assertIsNone(mock._methods, "methods not initialised correctly")
        self.assertEqual(mock._children, {}, "children not initialised incorrectly")
    
    def testUnicodeNotBroken(self):
        # This used to raise an exception with Python 2.5 and Mock 0.4
        unicode(Mock())
        
    def testReturnValueInConstructor(self):
        mock = Mock(return_value=None)
        self.assertIsNone(mock.return_value, "return value in constructor not honoured")
        
        
    def testSideEffect(self):
        mock = Mock()
        
        def effect(*args, **kwargs):
            raise SystemError('kablooie')
        
        mock.side_effect = effect
        self.assertRaises(SystemError, mock, 1, 2, fish=3)
        mock.assert_called_with(1, 2, fish=3)
        
        results = [1, 2, 3]
        def effect():
            return results.pop()
        mock.side_effect = effect
        
        self.assertEqual([mock(), mock(), mock()], [3, 2, 1],
                          "side effect not used correctly")

        mock = Mock(side_effect=sentinel.SideEffect)
        self.assertEqual(mock.side_effect, sentinel.SideEffect,
                          "side effect in constructor not used")
        
        def side_effect():
            return DEFAULT
        mock = Mock(side_effect=side_effect, return_value=sentinel.RETURN)
        self.assertEqual(mock(), sentinel.RETURN)
        
        
    def testReset(self):
        parent = Mock()
        spec = ["something"]
        mock = Mock(name="child", parent=parent, spec=spec)
        mock(sentinel.Something, something=sentinel.SomethingElse)
        something = mock.something
        mock.something()
        mock.side_effect = sentinel.SideEffect
        return_value = mock.return_value
        return_value()
        
        mock.reset_mock()
        
        self.assertEqual(mock._name, "child", "name incorrectly reset")
        self.assertEqual(mock._parent, parent, "parent incorrectly reset")
        self.assertEqual(mock._methods, spec, "methods incorrectly reset")
        
        self.assertFalse(mock.called, "called not reset")
        self.assertEqual(mock.call_count, 0, "call_count not reset")
        self.assertEqual(mock.call_args, None, "call_args not reset")
        self.assertEqual(mock.call_args_list, [], "call_args_list not reset")
        self.assertEqual(mock.method_calls, [], 
                          "method_calls not initialised correctly: %r != %r" % (mock.method_calls, []))
        
        self.assertEqual(mock.side_effect, sentinel.SideEffect,
                          "side_effect incorrectly reset")
        self.assertEqual(mock.return_value, return_value,
                          "return_value incorrectly reset")
        self.assertFalse(return_value.called, "return value mock not reset")
        self.assertEqual(mock._children, {'something': something}, 
                          "children reset incorrectly")
        self.assertEqual(mock.something, something,
                          "children incorrectly cleared")
        self.assertFalse(mock.something.called, "child not reset")
        
    
    def testCall(self):
        mock = Mock()
        self.assertTrue(isinstance(mock.return_value, Mock), "Default return_value should be a Mock")
        
        result = mock()
        self.assertEqual(mock(), result, "different result from consecutive calls")
        mock.reset_mock()
        
        ret_val = mock(sentinel.Arg)
        self.assertTrue(mock.called, "called not set")
        self.assertEqual(mock.call_count, 1, "call_count incoreect")
        self.assertEqual(mock.call_args, ((sentinel.Arg,), {}), "call_args not set")
        self.assertEqual(mock.call_args_list, [((sentinel.Arg,), {})], "call_args_list not initialised correctly")

        mock.return_value = sentinel.ReturnValue
        ret_val = mock(sentinel.Arg, key=sentinel.KeyArg)
        self.assertEqual(ret_val, sentinel.ReturnValue, "incorrect return value")
                          
        self.assertEqual(mock.call_count, 2, "call_count incorrect")
        self.assertEqual(mock.call_args, ((sentinel.Arg,), {'key': sentinel.KeyArg}), "call_args not set")
        self.assertEqual(mock.call_args_list, [((sentinel.Arg,), {}), ((sentinel.Arg,), {'key': sentinel.KeyArg})], "call_args_list not set")

    def testCallArgsComparison(self):
        mock = Mock()
        mock()
        mock(sentinel.Arg)
        mock(kw=sentinel.Kwarg)
        mock(sentinel.Arg, kw=sentinel.Kwarg)
        self.assertEqual(mock.call_args_list, [(),
                                                ((sentinel.Arg,),),
                                                ({"kw": sentinel.Kwarg},),
                                                ((sentinel.Arg,), {"kw": sentinel.Kwarg})])
        self.assertEqual(mock.call_args, ((sentinel.Arg,), {"kw": sentinel.Kwarg}))

    def testAssertCalledWith(self):
        mock = Mock()
        mock()
        
        # Will raise an exception if it fails
        mock.assert_called_with()
        self.assertRaises(AssertionError, mock.assert_called_with, 1)
        
        mock.reset_mock()
        self.assertRaises(AssertionError, mock.assert_called_with)
        
        mock(1, 2, 3, a='fish', b='nothing')        
        mock.assert_called_with(1, 2, 3, a='fish', b='nothing')

        
    def testAttributeAccessReturnsMocks(self):
        mock = Mock()
        something = mock.something
        self.assertTrue(isinstance(something, Mock), "attribute isn't a mock")
        self.assertEqual(mock.something, something, "different attributes returned for same name")
        
        # Usage example
        mock = Mock()
        mock.something.return_value = 3
        
        self.assertEqual(mock.something(), 3, "method returned wrong value")
        self.assertTrue(mock.something.called, "method didn't record being called")
        

    def testAttributesHaveNameAndParentSet(self):
        mock = Mock()
        something = mock.something
        
        self.assertEqual(something._name, "something", "attribute name not set correctly")
        self.assertEqual(something._parent, mock, "attribute parent not set correctly")


    def testMethodCallsRecorded(self):
        mock = Mock()
        mock.something(3, fish=None)
        mock.something_else.something(6, cake=sentinel.Cake)
        
        self.assertEqual(mock.something_else.method_calls,
                          [("something", (6,), {'cake': sentinel.Cake})],
                          "method calls not recorded correctly")
        self.assertEqual(mock.method_calls,
                          [("something", (3,), {'fish': None}),
                           ("something_else.something", (6,), {'cake': sentinel.Cake})],
                          "method calls not recorded correctly")

    def testMethodCallsCompareEasily(self):
        mock = Mock()
        mock.something()
        self.assertEqual(mock.method_calls, [('something',)])
        self.assertEqual(mock.method_calls, [('something', (), {})])

        mock = Mock()
        mock.something('different')
        self.assertEqual(mock.method_calls, [('something', ('different',))])
        self.assertEqual(mock.method_calls, [('something', ('different',), {})])

        mock = Mock()
        mock.something(x=1)
        self.assertEqual(mock.method_calls, [('something', {'x': 1})])
        self.assertEqual(mock.method_calls, [('something', (), {'x': 1})])

        mock = Mock()
        mock.something('different', some='more')
        self.assertEqual(mock.method_calls, [('something', ('different',), {'some': 'more'})])

    def testOnlyAllowedMethodsExist(self):
        spec = ["something"]
        mock = Mock(spec=spec)
        
        # this should be allowed
        mock.something
        self.assertRaisesRegexp(AttributeError, 
                                     "Mock object has no attribute 'something_else'",
                                     lambda: mock.something_else)

    
    def testFromSpec(self):
        class Something(object):
            x = 3
            __something__ = None
            def y(self):
                pass
        
        def testAttributes(mock):
            # should work
            mock.x
            mock.y
            self.assertRaisesRegexp(AttributeError, 
                                         "Mock object has no attribute 'z'",
                                         lambda: mock.z)
            self.assertRaisesRegexp(AttributeError, 
                                         "Mock object has no attribute '__something__'",
                                         lambda: mock.__something__)
            
        testAttributes(Mock(spec=Something))
        testAttributes(Mock(spec=Something()))
        

    def testWrapsCalls(self):
        real = Mock()
        
        mock = Mock(wraps=real)
        self.assertEqual(mock(), real())
        
        real.reset_mock()
        
        mock(1, 2, fish=3)
        real.assert_called_with(1, 2, fish=3)


    def testWrapsCallWithNonDefaultReturnValue(self):
        real = Mock()
        
        mock = Mock(wraps=real)
        mock.return_value = 3
        
        self.assertEqual(mock(), 3)
        self.assertFalse(real.called)
        
        
    def testWrapsAttributes(self):
        class Real(object):
            attribute = Mock()
            
        real = Real()
        
        mock = Mock(wraps=real)
        self.assertEqual(mock.attribute(), real.attribute())
        self.assertRaises(AttributeError, lambda: mock.fish)
        
        self.assertNotEqual(mock.attribute, real.attribute)
        result = mock.attribute.frog(1, 2, fish=3)
        Real.attribute.frog.assert_called_with(1, 2, fish=3)
        self.assertEqual(result, Real.attribute.frog())
        
        
    def testExceptionalSideEffect(self):
        mock = Mock(side_effect=AttributeError)
        self.assertRaises(AttributeError, mock)
        
        mock = Mock(side_effect=AttributeError('foo'))
        self.assertRaises(AttributeError, mock)
    
    def testBaseExceptionalSideEffect(self):
        mock = Mock(side_effect=KeyboardInterrupt)
        self.assertRaises(KeyboardInterrupt, mock)
        
        mock = Mock(side_effect=KeyboardInterrupt('foo'))
        self.assertRaises(KeyboardInterrupt, mock)
        
        
if __name__ == '__main__':
    unittest2.main()
    
