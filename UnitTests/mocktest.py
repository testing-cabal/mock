from testcase import TestCase
from testutils import RunTests

from mock import Mock, sentinel


class MockTest(TestCase):

    def testConstructor(self):
        mock = Mock()
        
        self.assertFalse(mock.called, "called not initialised correctly")
        self.assertEquals(mock.call_count, 0, "call_count not initialised correctly")
        self.assertNone(mock.return_value, "return_value not initialised correctly")
        
        self.assertEquals(mock.call_args, None, "call_args not initialised correctly")
        self.assertEquals(mock.call_args_list, [], "call_args_list not initialised correctly")
        self.assertEquals(mock.method_calls, [], 
                          "method_calls not initialised correctly")
        
        self.assertNone(mock._parent, "parent not initialised correctly")
        self.assertNone(mock._methods, "methods not initialised correctly")
        self.assertEquals(mock._children, {}, "children not initialised incorrectly")
        
        
    def testReset(self):
        parent = Mock()
        methods = ["something"]
        mock = Mock(name="child", parent=parent, methods=methods)
        mock(sentinel.Something, something=sentinel.SomethingElse)
        mock.something()
        
        mock.reset()
        
        self.assertEquals(mock._name, "child", "name incorrectly reset")
        self.assertEquals(mock._parent, parent, "parent incorrectly reset")
        self.assertEquals(mock._methods, methods, "methods incorrectly reset")
        
        self.assertFalse(mock.called, "called not reset")
        self.assertEquals(mock.call_count, 0, "call_count not reset")
        self.assertNone(mock.return_value, "return_value not reset")
        self.assertEquals(mock.call_args, None, "call_args not reset")
        self.assertEquals(mock.call_args_list, [], "call_args_list not reset")
        self.assertEquals(mock.method_calls, [], 
                          "method_calls not initialised correctly")
        
        self.assertEquals(mock._children, {}, "children not reset incorrectly")
        
    
    def testCall(self):
        mock = Mock()
        
        ret_val = mock(sentinel.Arg)
        self.assertNone(ret_val, "incorrect return value")
        
        self.assertTrue(mock.called, "called not set")
        self.assertEquals(mock.call_count, 1, "call_count incoreect")
        self.assertEquals(mock.call_args, ((sentinel.Arg,), {}), "call_args not set")
        self.assertEquals(mock.call_args_list, [((sentinel.Arg,), {})], "call_args_list not initialised correctly")

        mock.return_value = sentinel.ReturnValue
        ret_val = mock(sentinel.Arg, key=sentinel.KeyArg)
        self.assertEquals(ret_val, sentinel.ReturnValue, "incorrect return value")
                          
        self.assertEquals(mock.call_count, 2, "call_count incorrect")
        self.assertEquals(mock.call_args, ((sentinel.Arg,), {'key': sentinel.KeyArg}), "call_args not set")
        self.assertEquals(mock.call_args_list, [((sentinel.Arg,), {}), ((sentinel.Arg,), {'key': sentinel.KeyArg})], "call_args_list not set")
        

    def testAttributeAccessReturnsMocks(self):
        mock = Mock()
        something = mock.something
        self.assertTrue(isinstance(something, Mock), "attribute isn't a mock")
        self.assertEquals(mock.something, something, "different attributes returned for same name")
        
        # Usage example
        mock = Mock()
        mock.something.return_value = 3
        
        self.assertEquals(mock.something(), 3, "method returned wrong value")
        self.assertTrue(mock.something.called, "method didn't record being called")
        

    def testAttributesHaveNameAndParentSet(self):
        mock = Mock()
        something = mock.something
        
        self.assertEquals(something._name, "something", "attribute name not set correctly")
        self.assertEquals(something._parent, mock, "attribute parent not set correctly")


    def testMethodCallsRecorded(self):
        mock = Mock()
        mock.something(3, fish=None)
        mock.something_else.something(6, cake=sentinel.Cake)
        
        self.assertEquals(mock.something_else.method_calls,
                          [("something", (6,), {'cake': sentinel.Cake})],
                          "method calls not recorded correctly")
        self.assertEquals(mock.method_calls,
                          [("something", (3,), {'fish': None}),
                           ("something_else.something", (6,), {'cake': sentinel.Cake})],
                          "method calls not recorded correctly")
        
        
    def testOnlyAllowedMethodsExist(self):
        methods = ["something"]
        mock = Mock(methods=methods)
        
        # this should be allowed
        mock.something
        self.assertRaisesWithMessage(AttributeError, 
                                     "object has no attribute 'something_else'",
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
            self.assertRaisesWithMessage(AttributeError, 
                                         "object has no attribute 'z'",
                                         lambda: mock.z)
            self.assertRaisesWithMessage(AttributeError, 
                                         "object has no attribute '__something__'",
                                         lambda: mock.__something__)
            
        testAttributes(Mock(spec=Something))
        testAttributes(Mock(spec=Something()))
        

if __name__ == '__main__':
    RunTests(MockTest)
    
