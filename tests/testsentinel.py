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

this_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not this_dir in sys.path:
    sys.path.insert(0, this_dir)

from mock import sentinel, DEFAULT


class SentinelTest(unittest2.TestCase):

    def testSentinels(self):
        self.assertEquals(sentinel.whatever, sentinel.whatever, 'sentinel not stored')
        self.assertNotEquals(sentinel.whatever, sentinel.whateverelse, 'sentinel should be unique')
        
        
    def testSentinelName(self):
        self.assertEquals(str(sentinel.whatever), '<SentinelObject "whatever">', 'sentinel name incorrect')
        
    
    def testDEFAULT(self):
        self.assertTrue(DEFAULT is sentinel.DEFAULT)
    
    def testBases(self):
        # If this doesn't raise an AttributeError then help(mock) is broken
        self.assertRaises(AttributeError, lambda: sentinel.__bases__)


if __name__ == '__main__':
    unittest2.main()
    
