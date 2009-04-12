# Copyright (C) 2007-2009 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

from mocktest import MockTest
from sentineltest import SentinelTest
from patchtest import PatchTest

import sys
if sys.version_info[:2] >= (2, 5):
    from withtest import WithTest
del sys
