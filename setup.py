#! /usr/bin/python

# Copyright (C) 2007-2008 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock.html

from textwrap import dedent
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
    description = "A Python mock object library",
    long_description = dedent("""\
    There are already several Python mocking libraries available, so why another one?
    
    Most mocking libraries follow the 'record -> replay' pattern of mocking. I
    prefer the 'action -> assertion' pattern, which is more readable and intuitive
    particularly when working with the Python `unittest module
    <http://docs.python.org/lib/module-unittest.html>`_. For a discussion of the
    merits of the two approaches, see `Mocking, Patching, Stubbing: all that Stuff
    <http://www.voidspace.org.uk/python/articles/mocking.shtml>`_.
    
    ``mock`` provides a core ``Mock`` class that is intended to reduce the need to
    create a host of trivial stubs throughout your test suite. After performing an
    action, you can make assertions about which methods / attributes were used and
    arguments they were called with. You can also specify return values and set
    specific attributes in the normal way.
    
    It also provides a ``patch`` decorator that handles patching module and class
    level attributes within the scope of a test, along with ``sentinel`` for 
    creating unique objects."""),
    license = "BSD",
    keywords = "testing test mock mocking unittest patching stubs",
    url = "http://www.voidspace.org.uk/python/mock.html",
    download_url = 'http://www.voidspace.org.uk/downloads/mock-%s.zip' % __version__,

)
