# Copyright Michael Foord 2009
# Licensed under the BSD License
# See: http://pypi.python.org/pypi/discover

import optparse
import os
import re
import sys
import traceback
import types
import unittest

from fnmatch import fnmatch

if hasattr(types, 'ClassType'):
    class_types = (types.ClassType, type)
else:
    # for Python 3.0 compatibility
    class_types = type

__version__ = '0.3.0'

# what about .pyc or .pyo (etc)
# we would need to avoid loading the same tests multiple times
# from '.py', '.pyc' *and* '.pyo'
VALID_MODULE_NAME = re.compile(r'[_a-z]\w*\.py$', re.IGNORECASE)

def make_failed_import_test(name, suiteClass):
    message = 'Failed to import test module: %s' % name
    if hasattr(traceback, 'format_exc'):
        # Python 2.3 compatibility
        # format_exc returns two frames of discover.py as well
        message += '\n%s' % traceback.format_exc()
    
    def testImportFailure(self):
        raise ImportError(message)
    attrs = {name: testImportFailure}
    ModuleImportFailure = type('ModuleImportFailure', (unittest.TestCase,), attrs)
    return suiteClass((ModuleImportFailure(name),))


class DiscoveringTestLoader(unittest.TestLoader):
    """
    This class is responsible for loading tests according to various criteria
    and returning them wrapped in a TestSuite
    """
    _top_level_dir = None

    def loadTestsFromModule(self, module, use_load_tests=True):
        """Return a suite of all tests cases contained in the given module"""
        tests = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
                tests.append(self.loadTestsFromTestCase(obj))

        load_tests = getattr(module, 'load_tests', None)
        if use_load_tests and load_tests is not None:
            return load_tests(self, tests, None)
        return self.suiteClass(tests)


    def discover(self, start_dir, pattern='test*.py', top_level_dir=None):
        """Find and return all test modules from the specified start
        directory, recursing into subdirectories to find them. Only test files
        that match the pattern will be loaded. (Using shell style pattern
        matching.)

        All test modules must be importable from the top level of the project.
        If the start directory is not the top level directory then the top
        level directory must be specified separately.

        If a test package name (directory with '__init__.py') matches the
        pattern then the package will be checked for a 'load_tests' function. If
        this exists then it will be called with loader, tests, pattern.

        If load_tests exists then discovery does  *not* recurse into the package,
        load_tests is responsible for loading all tests in the package.

        The pattern is deliberately not stored as a loader attribute so that
        packages can continue discovery themselves. top_level_dir is stored so
        load_tests does not need to pass this argument in to loader.discover().
        """
        if top_level_dir is None and self._top_level_dir is not None:
            # make top_level_dir optional if called from load_tests in a package
            top_level_dir = self._top_level_dir
        elif top_level_dir is None:
            top_level_dir = start_dir

        top_level_dir = os.path.abspath(os.path.normpath(top_level_dir))
        start_dir = os.path.abspath(os.path.normpath(start_dir))

        if not top_level_dir in sys.path:
            # all test modules must be importable from the top level directory
            sys.path.append(top_level_dir)
        self._top_level_dir = top_level_dir

        if start_dir != top_level_dir and not os.path.isfile(os.path.join(start_dir, '__init__.py')):
            # what about __init__.pyc or pyo (etc)
            raise ImportError('Start directory is not importable: %r' % start_dir)

        tests = list(self._find_tests(start_dir, pattern))
        return self.suiteClass(tests)
    
    def _get_name_from_path(self, path):
        path = os.path.splitext(os.path.normpath(path))[0]
        
        _relpath = os.path.relpath(path, self._top_level_dir)
        assert not os.path.isabs(_relpath), "Path must be within the project"
        assert not _relpath.startswith('..'), "Path must be within the project"

        name = _relpath.replace(os.path.sep, '.')
        return name
    
    def _get_module_from_name(self, name):
        __import__(name)
        return sys.modules[name]

    def _find_tests(self, start_dir, pattern):
        """Used by discovery. Yields test suites it loads."""
        paths = os.listdir(start_dir)

        for path in paths:
            full_path = os.path.join(start_dir, path)
            if os.path.isfile(full_path):
                if not VALID_MODULE_NAME.match(path):
                    # valid Python identifiers only
                    continue
                
                if fnmatch(path, pattern):
                    # if the test file matches, load it
                    name = self._get_name_from_path(full_path)
                    try:
                        module = self._get_module_from_name(name)
                    except:
                        yield make_failed_import_test(name, self.suiteClass)
                    else:
                        yield self.loadTestsFromModule(module)
            elif os.path.isdir(full_path):
                if not os.path.isfile(os.path.join(full_path, '__init__.py')):
                    continue

                load_tests = None
                tests = None
                if fnmatch(path, pattern):
                    # only check load_tests if the package directory itself matches the filter
                    name = self._get_name_from_path(full_path)
                    package = self._get_module_from_path(name)
                    load_tests = getattr(package, 'load_tests', None)
                    tests = self.loadTestsFromModule(package, use_load_tests=False)

                if load_tests is None:
                    if tests is not None:
                        # tests loaded from package file
                        yield tests
                    # recurse into the package
                    for test in self._find_tests(full_path, pattern):
                        yield test
                else:
                    yield load_tests(self, tests, pattern)


##############################################
# relpath implementation taken from Python 2.7

if not hasattr(os.path, 'relpath'):
    if os.path is sys.modules.get('ntpath'):
        def relpath(path, start=os.path.curdir):
            """Return a relative version of a path"""
        
            if not path:
                raise ValueError("no path specified")
            start_list = os.path.abspath(start).split(os.path.sep)
            path_list = os.path.abspath(path).split(os.path.sep)
            if start_list[0].lower() != path_list[0].lower():
                unc_path, rest = os.path.splitunc(path)
                unc_start, rest = os.path.splitunc(start)
                if bool(unc_path) ^ bool(unc_start):
                    raise ValueError("Cannot mix UNC and non-UNC paths (%s and %s)"
                                                                        % (path, start))
                else:
                    raise ValueError("path is on drive %s, start on drive %s"
                                                        % (path_list[0], start_list[0]))
            # Work out how much of the filepath is shared by start and path.
            for i in range(min(len(start_list), len(path_list))):
                if start_list[i].lower() != path_list[i].lower():
                    break
            else:
                i += 1
        
            rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
            if not rel_list:
                return os.path.curdir
            return os.path.join(*rel_list)
    
    else:
        # default to posixpath definition
        def relpath(path, start=os.path.curdir):
            """Return a relative version of a path"""
        
            if not path:
                raise ValueError("no path specified")
        
            start_list = os.path.abspath(start).split(os.path.sep)
            path_list = os.path.abspath(path).split(os.path.sep)
        
            # Work out how much of the filepath is shared by start and path.
            i = len(os.path.commonprefix([start_list, path_list]))
        
            rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
            if not rel_list:
                return os.path.curdir
            return os.path.join(*rel_list)
        
    os.path.relpath = relpath

#############################################


USAGE = """\
Usage: discover.py [options]

Options:
  -v, --verbose    Verbose output
  -s directory     Directory to start discovery ('.' default)
  -p pattern       Pattern to match test files ('test*.py' default)
  -t directory     Top level directory of project (default to
                   start directory)

For test discovery all test modules must be importable from the top
level directory of the project.
"""

def _usage_exit(msg=None):
    if msg:
        print (msg)
    print (USAGE)
    sys.exit(2)


def _do_discovery(argv, verbosity, Loader):
    # handle command line args for test discovery
    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbose', dest='verbose', default=False,
                      help='Verbose output', action='store_true')
    parser.add_option('-s', '--start-directory', dest='start', default='.',
                      help="Directory to start discovery ('.' default)")
    parser.add_option('-p', '--pattern', dest='pattern', default='test*.py',
                      help="Pattern to match tests ('test*.py' default)")
    parser.add_option('-t', '--top-level-directory', dest='top', default=None,
                      help='Top level directory of project (defaults to start directory)')

    options, args = parser.parse_args(argv)
    if len(args) > 3:
        _usage_exit()

    for name, value in zip(('start', 'pattern', 'top'), args):
        setattr(options, name, value)

    if options.verbose:
        verbosity = 2

    start_dir = options.start
    pattern = options.pattern
    top_level_dir = options.top

    loader = Loader()
    return loader.discover(start_dir, pattern, top_level_dir), verbosity


def _run_tests(tests, testRunner, verbosity, exit):
    if isinstance(testRunner, class_types):
        try:
            testRunner = testRunner(verbosity=verbosity)
        except TypeError:
            # didn't accept the verbosity argument
            testRunner = testRunner()
    result = testRunner.run(tests)
    if exit:
        sys.exit(not result.wasSuccessful())
    return result


def main(argv=None, testRunner=None, testLoader=None, exit=True, verbosity=1):
    if testLoader is None:
        testLoader = DiscoveringTestLoader
    if testRunner is None:
        testRunner = unittest.TextTestRunner
    if argv is None:
        argv = sys.argv[1:]

    tests, verbosity = _do_discovery(argv, verbosity, testLoader)
    return _run_tests(tests, testRunner, verbosity, exit)


if __name__ == '__main__':
    if sys.argv[0] is None:
        # fix for weird behaviour when run with python -m
        # from a zipped egg.
        sys.argv[0] = 'discover.py'
    main()
    
"""
This module has the following improvements over what is currently in the
Python standard library:

* Failure to import a module does not halt discovery
* Will not attempt to import test files whose names are not valid Python
  identifiers, even if they match the pattern.

"""