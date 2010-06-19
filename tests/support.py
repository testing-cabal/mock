import sys

info = sys.version_info
if info[:3] >= (3, 2, 0) or info[0] == 2 and info[1] >= 7:
    # for Python 2.7 and 3.2 ordinary unittest is fine
    import unittest as unittest2
else:
    import unittest2


try:
    apply = apply
except NameError:
    # no apply in Python 3
    def apply(f, *args, **kw):
        f(*args, **kw)


inPy3k = sys.version_info[0] == 3


class SomeClass(object):
    class_attribute = None
    
    def wibble(self):
        pass
