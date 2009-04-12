# Copyright (C) 2007-2009 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

import unittest
import sys
from types import ModuleType


def IsTestCase(test):
    if type(test) == type and issubclass(test, unittest.TestCase):
        return True
    return False
    
    
def AddTests(suite, test):
    if isinstance(test, ModuleType):
        for entry in test.__dict__.values():
            if IsTestCase(entry):
                suite.addTests(unittest.makeSuite(entry))
    elif IsTestCase(test):
        suite.addTests(unittest.makeSuite(test))


def MakeSuite(*tests):
    suite = unittest.TestSuite()
    for test in tests:
        AddTests(suite, test)
    return suite


def RunTests(*tests, **keywargs):
    suite = keywargs.get('suite')
    if suite is None:
        suite = MakeSuite(*tests)
    else:
        del keywargs['suite']
    return unittest.TextTestRunner(**keywargs).run(suite)

