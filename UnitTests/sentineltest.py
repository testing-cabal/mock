from testcase import TestCase
from testutils import RunTests

from mock import sentinel


class SentinelTest(TestCase):

    def testSentinels(self):
        self.assertEquals(sentinel.whatever, sentinel.whatever, 'sentinel not stored')
        self.assertNotEquals(sentinel.whatever, sentinel.whateverelse, 'sentinel should be unique')
        
        
    def testSentinelName(self):
        self.assertEquals(str(sentinel.whatever), '<SentinelObject "whatever">', 'sentinel name incorrect')
        


if __name__ == '__main__':
    RunTests(SentinelTest)
