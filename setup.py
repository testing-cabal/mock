#! /usr/bin/python

# Copyright (C) 2007-2010 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk
# http://www.voidspace.org.uk/python/mock/

from mock import __version__

from distutils.core import setup
import os


NAME = 'mock'
MODULES = ['mock']
DESCRIPTION = 'A Python Mocking and Patching Library for Testing'

URL = "http://www.voidspace.org.uk/python/mock/"
'http://www.voidspace.org.uk/downloads/mock-%s.zip' % __version__

readme = os.path.join(os.path.dirname(__file__), 'README.txt')
LONG_DESCRIPTION = open(readme).read()

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.4',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Testing',
]

AUTHOR = 'Michael Foord'
AUTHOR_EMAIL = 'michael@voidspace.org.uk'
KEYWORDS = "testing test mock mocking unittest patching stubs fakes doubles".split(' ')

DOWNLOAD_URL = 'http://www.voidspace.org.uk/downloads/mock-0.7.0.zip'

setup(
    name=NAME,
    version=__version__,
    py_modules=MODULES,
    
    # metadata for upload to PyPI
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords=KEYWORDS,
    url=URL,
    download_url=DOWNLOAD_URL,
    classifiers=CLASSIFIERS,
)
