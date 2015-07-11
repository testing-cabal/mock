#!/usr/bin/env python
from distutils.version import StrictVersion
import setuptools
import sys


def _verify_compatible_setuptools():
    '''
    mock requires setuptools>=17.1. We explicitly do not put this in
    setup_requires because we don't want to force users to upgrade setuptools.
    Instead fail during install time and tell user about this constraint.
    '''
    setuptools_required = StrictVersion("17.1")
    setuptools_installed = StrictVersion(setuptools.version.__version__)

    if setuptools_installed < setuptools_required:
        sys.stderr.write(
            "mock requires setuptools>=17.1. Aborting installation\n")
        sys.exit(1)

_verify_compatible_setuptools()

setuptools.setup(
    setup_requires=['pbr'],
    pbr=True)
