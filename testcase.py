# Copyright (C) 2007-2009 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

import unittest


class TestCase(unittest.TestCase):
        
    def assertTrue(self, actual, message=None):
        if not isinstance(actual, bool) or not actual:
            msg = "%s is not True" % actual
            if message:
                msg = msg + ': ' + message
            raise AssertionError(msg)


    def assertFalse(self, actual, message=None):
        if not isinstance(actual, bool) or actual:
            msg = "%s is not False" % actual
            if message:
                msg = msg + ': ' + message
            raise AssertionError(msg)
            
            
    def assertNone(self, value, message=None):
        if value is not None:
            msg = "%s is not None" % value
            if message:
                msg = msg + ': ' + message
            raise AssertionError(msg)
        
        
    def assertNotNone(self, value, message=None):
        if value is None:
            msg = "Expected non-None value" % actual
            if message:
                msg = msg + ': ' + message
            raise AssertionError(msg)


    def assertRaisesWithMessage(self, excClass, message, callableObj, *args, **kwargs):
        e = None
        actualMsg = None
        try:
            callableObj(*args, **kwargs)
        except excClass, e:
            actualMsg = str(e)
            if actualMsg == message:
                return
        except Exception, e:
            pass
        
        if e is None:
            raise AssertionError("No exception raised. Expected %s" % excClass.__name__)
        if actualMsg is not None:
            raise AssertionError("Incorrect exception message. Actual: %s\nExpected: %s" % (actualMsg, message)) 
        raise AssertionError("Incorrect exception type. Actual: %s. Expected: %s" % (e.__class__.__name__, excClass.__name__))
    