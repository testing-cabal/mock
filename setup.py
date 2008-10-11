#! /usr/bin/python

from setuptools import setup, find_packages
from mock import __version__

setup(
    name = "mock",
    version = __version__,
    packages = [],
    py_modules = ['mock'],
    include_package_data = False,
    zip_safe = True,
    
    # metadata for upload to PyPI
    author = "Michael Foord",
    author_email = "fuzzyman@voidspace.org.uk",
    description = "This is an Example Package",
    license = "BSD",
    keywords = "testing test mock mocking unittest patching stubs",
    url = "http://www.voidspace.org.uk/python/mock.html",

    # could also include long_description, download_url, classifiers, etc.
)
