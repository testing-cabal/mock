import sys

info = sys.version_info
if info[:3] >= (3, 2, 0):
    # for Python 3.2 ordinary unittest is fine
    import unittest as unittest2
else:
    import unittest2


inPy3k = sys.version_info[0] == 3
with_available = sys.version_info[:2] >= (2, 5)


class SomeClass(object):
    class_attribute = None

    def wibble(self):
        pass