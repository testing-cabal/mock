mock is a library for testing in Python. It allows you to replace parts of
your system under test with mock objects and make assertions about how they
have been used.

mock is now part of the Python standard library, available as `unittest.mock
<https://docs.python.org/dev/library/unittest.mock.html>`_ in Python 3.3
onwards.

This package contains a rolling backport of the standard library mock code
compatible with Python 2.7 and up, and 3.2 and up.

Please see the standard library documentation for more details.

mock is CI tested using Travis-CI on Python versions 2.7, 3.2, 3.3, 3.4, 3.5,
nightly Python 3 builds, pypy, pypy3. Jython support is desired, if
someone could contribute a patch to .travis.jml to support it that would be
excellent.

The last release of mock to support 2.6 was 1.0.1. mock 1.1.0 and above require
Python 2.7 or higher.

NEWS entries from cPython:

.. include:: NEWS

Notes for maintainers
---------------------

Releasing
=========

2. tag -s, push --tags origin master
3. setup.py sdist bdist_wheel upload -s

Backporting rules
=================

type -> ClassTypes
__self__ -> self
name.isidentifier() -> _isidentifier(name)
super -> _super

