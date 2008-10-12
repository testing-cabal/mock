# Copyright (C) 2007-2008 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock.html

import os
import sys

if not os.getcwd() in sys.path:
    sys.path.append(os.getcwd())

import UnitTests

from testutils import MakeSuite, RunTests

tests = MakeSuite(UnitTests)
RunTests(suite=tests, verbosity=2)
