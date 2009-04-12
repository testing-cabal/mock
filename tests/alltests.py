# Copyright (C) 2007-2009 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

import os
import sys

if not os.getcwd() in sys.path:
    sys.path.append(os.getcwd())

import tests

from testutils import MakeSuite, RunTests

suite = MakeSuite(tests)
RunTests(suite=suite, verbosity=2)
