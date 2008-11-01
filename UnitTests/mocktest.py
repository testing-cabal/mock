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

from mock import Mock, sentinel, MakeMock


class MockTest(TestCase):

    def testConstructor(self):
        mock = Mock()
        
        self.assertFalse(mock.called, "called not initialised correctly")
        self.assertEquals(mock.call_count, 0, "call_count not initialised correctly")
        self.assertTrue(isinstance(mock.return_value, Mock), "return_value not initialised correctly")
        
        self.assertEquals(mock.call_args, None, "call_args not initialised correctly")
        self.assertEquals(mock.call_args_list, [], "call_args_list not initialised correctly")
        self.assertEquals(mock.method_calls, [], 
                          "method_calls not initialised correctly")
        
        # Can't use hasattr for this test as it always returns True on a mock...
        self.assertFalse('_items' in mock.__dict__, "default mock should not have '_items' attribute")
        
        self.assertNone(mock._parent, "parent not initialised correctly")
        self.assertNone(mock._methods, "methods not initialised correctly")
        self.assertEquals(mock._children, {}, "children not initialised incorrectly")
        
        
    def testReturnValueInConstructor(self):
        mock = Mock(return_value=None)
        self.assertNone(mock.return_value, "return value in constructor not honoured")
        
        
    def testSideEffect(self):
        mock = Mock()
        
        def effect():
            raise SystemError('kablooie')
        
        mock.side_effect = effect
        self.assertRaises(SystemError, mock)
        self.assertTrue(mock.called, "call not recorded")
        
        results = [1, 2, 3]
        def effect():
            mock.return_value = results.pop()
        mock.side_effect = effect
        
        self.assertEquals([mock(), mock(), mock()], [3, 2, 1],
                          "side effect not used correctly")

        mock = Mock(side_effect=sentinel.SideEffect)
        self.assertEquals(mock.side_effect, sentinel.SideEffect,
                          "side effect in constructor not used")
        
        
    def testReset(self):
        parent = Mock()
        methods = ["something"]
        mock = Mock(name="child", parent=parent, methods=methods)
        mock(sentinel.Something, something=sentinel.SomethingElse)
        something = mock.something
        mock.something()
        mock.side_effect = sentinel.SideEffect
        return_value = mock.return_value
        return_value()
        
        mock.reset()
        
        self.assertEquals(mock._name, "child", "name incorrectly reset")
        self.assertEquals(mock._parent, parent, "parent incorrectly reset")
        self.assertEquals(mock._methods, methods, "methods incorrectly reset")
        
        self.assertFalse(mock.called, "called not reset")
        self.assertEquals(mock.call_count, 0, "call_count not reset")
        self.assertEquals(mock.call_args, None, "call_args not reset")
        self.assertEquals(mock.call_args_list, [], "call_args_list not reset")
        self.assertEquals(mock.method_calls, [], 
                          "method_calls not initialised correctly")
        
        self.assertEquals(mock.side_effect, sentinel.SideEffect,
                          "side_effect incorrectly reset")
        self.assertEquals(mock.return_value, return_value,
                          "return_value incorrectly reset")
        self.assertFalse(return_value.called, "return value mock not reset")
        self.assertEquals(mock._children, {'something': something}, 
                          "children reset incorrectly")
        self.assertEquals(mock.something, something,
                          "children incorrectly cleared")
        self.assertFalse(mock.something.called, "child not reset")
        
    
    def testCall(self):
        mock = Mock()
        self.assertTrue(isinstance(mock.return_value, Mock), "Default return_value should be a Mock")
        
        result = mock()
        self.assertEquals(mock(), result, "different result from consecutive calls")
        mock.reset()
        
        ret_val = mock(sentinel.Arg)
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
        
    
    def testAssertCalledWith(self):
        mock = Mock()
        mock()
        
        # Will raise an exception if it fails
        mock.assert_called_with()
        self.assertRaises(AssertionError, mock.assert_called_with, 1)
        
        mock.reset()
        self.assertRaises(AssertionError, mock.assert_called_with)
        
        mock(1, 2, 3, a='fish', b='nothing')        
        mock.assert_called_with(1, 2, 3, a='fish', b='nothing')

        
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
        

    def testMakeMockBasic(self):
        Class = MakeMock([])
        self.assertTrue(issubclass(Class, Mock))
        
        self.assertRaisesWithMessage(NameError, "Unknown magic method 'frob'",
                                     MakeMock, ['frob'])
        
        
    def testMakeMockGetItem(self):
        Class = MakeMock(['getitem'])
        self.assertTrue(hasattr(Class, '__getitem__'))
        self.assertFalse(hasattr(Class, '__setitem__'))
        
        self.assertEquals(Class()._items, {})
        
        instance = Class(items={0: 'fish', 1: 'trouble'})
        self.assertEquals(instance._items, {0: 'fish', 1: 'trouble'})
        self.assertEquals(instance[0], 'fish')
        self.assertEquals(instance[1], 'trouble')
        self.assertRaises(KeyError, lambda: instance[2])
        
        self.assertEquals(instance.method_calls,
                          [('__getitem__', (0,), {}),
                           ('__getitem__', (1,), {})])
        
        instance = Class(items=[3, 2, 1])
        self.assertEquals(instance._items, [3, 2, 1])
        self.assertEquals(instance[0], 3)
        self.assertEquals(instance[1], 2)
        self.assertRaises(IndexError, lambda: instance[3])
        
        
    def testMakeMockSetItem(self):
        Class = MakeMock(['setitem'])
        self.assertTrue(hasattr(Class, '__setitem__'))
        self.assertFalse(hasattr(Class, '__getitem__'))
                
        instance = Class()
        self.assertEquals(instance._items, {})
        instance[0] = 'fish'
        instance[1] = 'trouble'
        
        self.assertEquals(instance.method_calls,
                          [('__setitem__', (0, 'fish'), {}),
                           ('__setitem__', (1, 'trouble'), {})])
        
        self.assertEquals(instance._items, {0: 'fish', 1: 'trouble'})
        
        
    def testMakeMockDelItem(self):
        Class = MakeMock(['delitem'])
        self.assertTrue(hasattr(Class, '__delitem__'))
                
        instance = Class(items={'fish': 'eggs'})
        del instance['fish']
        self.assertEquals(instance._items, {})
        
        self.assertEquals(instance.method_calls,
                          [('__delitem__', ('fish',), {})])
        
    
    def testMakeMockIter(self):
        Class = MakeMock(['iter'])
        self.assertTrue(hasattr(Class, '__iter__'))

        self.assertEquals(Class()._items, {})
                
        instance = Class(items=[6, 5])
        self.assertEquals(list(instance), [6, 5])
        self.assertEquals(instance.method_calls,
                          [('__iter__', (), {})])    


    def testSpecClassesImplementMagicMethods(self):
        class Something(object):
            def __getitem__(self, key):
                pass
            def __setitem__(self, key, value):
                pass
            def __iter__(self):
                pass
            
        mock = Mock(spec=Something)
        self.assertEquals(mock._items, {})
        mock._items = [3, 2, 1]
        self.assertEquals(list(mock), [3, 2, 1])
        self.assertEquals(mock[1], 2)
        mock[1] = 4
        self.assertEquals(list(mock), [3, 4, 1])
        
        
    def testMethodsArgumentCreatesMagicMethods(self):
        mock = Mock(methods=['__getitem__', '__setitem__', '__iter__'])
        self.assertEquals(mock._items, {})
        mock._items = [3, 2, 1]
        self.assertEquals(list(mock), [3, 2, 1])
        self.assertEquals(mock[1], 2)
        mock[1] = 4
        self.assertEquals(list(mock), [3, 4, 1])
        
    
    def testMakeMockLen(self):
        Class = MakeMock(['len'])
        self.assertTrue(hasattr(Class, '__len__'))

        instance = Class()
        self.assertEquals(len(instance), 0)
        self.assertEquals(instance.method_calls,
                          [('__len__', (), {})])    
        
        instance.reset()
        instance._items = 1, 2, 3
        self.assertEquals(len(instance), 3)
        
    
    def testMakeMockContains(self):
        Class = MakeMock(['contains'])
        self.assertTrue(hasattr(Class, '__contains__'))

        instance = Class()
        self.assertFalse(3 in instance) 
        self.assertEquals(instance.method_calls,
                          [('__contains__', (), {})])    
        
        instance.reset()
        instance._items = 1, 2, 3
        self.assertTrue(3 in instance)
        
    
    def testMakeMockNonZero(self):
        Class = MakeMock(['nonzero'])
        self.assertTrue(hasattr(Class, '__nonzero__'))

        instance = Class()
        self.assertFalse(bool(instance)) 
        self.assertEquals(instance.method_calls,
                          [('__nonzero__', (), {})])    
        
        instance.reset()
        instance._items = 1, 2, 3
        self.assertTrue(bool(instance)) 
        


        

"""
Keyword arguments to patch and patch_object to create a 
comparable or container like Mock - or Mock with methods
or spec. (spec, methods, cmp, container).

Should a failed indexing attempt still be added to 'method_calls'?
(Currently not.)

Should reset affect '_items'? Take a copy of the items and restore
it.

Parent method calls if magic methods called on a child?

Should attributes (children) on mocks created from MakeMock be plain 'Mock' or from the
same class as their parent? (currently they are plain mocks)

Still to implement:

    __hash__
    comparisons
    __delitem__
    
    numeric types
    
    unary operators
    
    context managers - enter, exit
    
    descriptors - get, set, delete
    
    
    
"""
        
if __name__ == '__main__':
    RunTests(MockTest)
    
