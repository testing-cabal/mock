#!/usr/bin/env python
from distutils.version import StrictVersion
import setuptools
import sys


# Setuptools 17.1 is required, and setup_requires cannot upgrade setuptools
# in-place, nor trigger the use of a newer version. Abort cleanly up-front.
setuptools_required = StrictVersion("17.1")
setuptools_installed = StrictVersion(setuptools.__version__)
if setuptools_installed < setuptools_required:
    sys.stderr.write(
        "mock requires setuptools>=17.1. Aborting installation\n")
    sys.exit(1)

setuptools.setup(
    setup_requires=['pbr>=1.3'],
    pbr=True)
