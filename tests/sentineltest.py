# Copyright (C) 2007-2009 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

import os
import sys
this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not this_dir in sys.path:
    sys.path.insert(0, this_dir)

from testcase import TestCase
from testutils import RunTests

from mock import sentinel, DEFAULT


class SentinelTest(TestCase):

    def testSentinels(self):
        self.assertEquals(sentinel.whatever, sentinel.whatever, 'sentinel not stored')
        self.assertNotEquals(sentinel.whatever, sentinel.whateverelse, 'sentinel should be unique')
        
        
    def testSentinelName(self):
        self.assertEquals(str(sentinel.whatever), '<SentinelObject "whatever">', 'sentinel name incorrect')
        
    
    def testDEFAULT(self):
        self.assertTrue(DEFAULT is sentinel.DEFAULT)
        


if __name__ == '__main__':
    RunTests(SentinelTest)
