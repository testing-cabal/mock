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
creating unique objects.

Mock is tested on Python 2.4-2.6.

A version of Mock that supports mocking magic methods is in the subversion
repository. This will be released as version 0.7 when the docs are complete:
http://code.google.com/p/mock/source/browse/trunk/mock.py

In the meantime, information on mocking magic methods is available at:
http://www.voidspace.org.uk/python/weblog/arch_d7_2010_01_02.shtml#e1143
