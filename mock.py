# mock.py
# Test tools for mocking and patching.
# Copyright (C) 2007-2010 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk

# mock 0.6.0
# http://www.voidspace.org.uk/python/mock/

# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/python/license.shtml

# Scripts maintained at http://www.voidspace.org.uk/python/index.shtml
# Comments, suggestions and bug reports welcome.


__all__ = (
    'Mock',
    'mocksignature',
    'patch',
    'patch_object',
    'sentinel',
    'DEFAULT'
)

__version__ = '0.7.0'

try:
    import inspect
except ImportError:
    # for alternative platforms that
    # may not have inspect
    inspect = None


# getsignature and mocksignature heavily "inspired" by
# the decorator module: http://pypi.python.org/pypi/decorator/
# by Michele Simionato

def _getsignature(func):
    if inspect is None:
        raise ImportError('inspect module not available')
    assert inspect.ismethod(func) or inspect.isfunction(func)
    regargs, varargs, varkwargs, defaults = inspect.getargspec(func)

    # instance methods need to lose the self argument
    im_self = getattr(func, 'im_self', None)
    if im_self is not None:
        regargs = regargs[1:]

    argnames = list(regargs)
    if varargs:
        argnames.append(varargs)
    if varkwargs:
        argnames.append(varkwargs)
    assert '_mock_' not in argnames, ("_mock_ is a reserved argument name, can't mock signatures using _mock_")
    signature = inspect.formatargspec(regargs, varargs, varkwargs, defaults, formatvalue=lambda value: "")
    return signature[1:-1]


def _copy_func_details(func, funcopy):
    funcopy.__name__ = func.__name__
    funcopy.__doc__ = func.__doc__
    funcopy.__dict__.update(func.__dict__)
    funcopy.__module__ = func.__module__
    funcopy.func_defaults = func.func_defaults


def mocksignature(func, mock):
    signature = _getsignature(func)
    src = "lambda %(signature)s: _mock_(%(signature)s)" % {'signature': signature}

    funcopy = eval(src, dict(_mock_=mock))
    _copy_func_details(func, funcopy)
    return funcopy



def _is_magic(name):
    return '__%s__' % name[2:-2] == name


class SentinelObject(object):
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return '<SentinelObject "%s">' % self.name


class Sentinel(object):
    def __init__(self):
        self._sentinels = {}
        
    def __getattr__(self, name):
        if name == '__bases__':
            # Without this help(mock) raises an exception
            raise AttributeError
        return self._sentinels.setdefault(name, SentinelObject(name))
    
    
sentinel = Sentinel()

DEFAULT = sentinel.DEFAULT

class OldStyleClass:
    pass
ClassType = type(OldStyleClass)

def _copy(value):
    if type(value) in (dict, list, tuple, set):
        return type(value)(value)
    return value


class Mock(object):
    
    def __new__(cls, *args, **kw):
        class Mock(cls):
            # every instance has its own class
            # so we can create magic methods on the
            # class without stomping on other mocks
            pass
        return object.__new__(Mock)
        
    def __init__(self, spec=None, side_effect=None, return_value=DEFAULT, 
                 name=None, parent=None, wraps=None):
        self._parent = parent
        self._name = name
        if spec is not None and not isinstance(spec, list):
            spec = [member for member in dir(spec) if not _is_magic(member)]
        
        self._methods = spec
        self._children = {}
        self._return_value = return_value
        self.side_effect = side_effect
        self._wraps = wraps
        
        self.reset_mock()
        

    def reset_mock(self):
        self.called = False
        self.call_args = None
        self.call_count = 0
        self.call_args_list = []
        self.method_calls = []
        for child in self._children.itervalues():
            child.reset_mock()
        if isinstance(self._return_value, Mock):
            self._return_value.reset_mock()
        
    
    def __get_return_value(self):
        if self._return_value is DEFAULT:
            self._return_value = Mock()
        return self._return_value
    
    def __set_return_value(self, value):
        self._return_value = value
        
    return_value = property(__get_return_value, __set_return_value)


    def __call__(self, *args, **kwargs):
        self.called = True
        self.call_count += 1
        self.call_args = (args, kwargs)
        self.call_args_list.append((args, kwargs))
        
        parent = self._parent
        name = self._name
        while parent is not None:
            parent.method_calls.append((name, args, kwargs))
            if parent._parent is None:
                break
            name = parent._name + '.' + name
            parent = parent._parent
        
        ret_val = DEFAULT
        if self.side_effect is not None:
            if (isinstance(self.side_effect, Exception) or 
                isinstance(self.side_effect, (type, ClassType)) and
                issubclass(self.side_effect, Exception)):
                raise self.side_effect
            
            ret_val = self.side_effect(*args, **kwargs)
            if ret_val is DEFAULT:
                ret_val = self.return_value
        
        if self._wraps is not None and self._return_value is DEFAULT:
            return self._wraps(*args, **kwargs)
        if ret_val is DEFAULT:
            ret_val = self.return_value
        return ret_val
    
    
    def __getattr__(self, name):
        if self._methods is not None:
            if name not in self._methods:
                raise AttributeError("Mock object has no attribute '%s'" % name)
        elif _is_magic(name):
            raise AttributeError(name)
        
        if name not in self._children:
            wraps = None
            if self._wraps is not None:
                wraps = getattr(self._wraps, name)
            self._children[name] = Mock(parent=self, name=name, wraps=wraps)
            
        return self._children[name]
    
    def __setattr__(self, name, value):
        if name in _all_magics:
            setattr(self.__class__, name, get_method(name, value))
            original = value
            def value(*args, **kw):
                return original(self, *args, **kw)
            _copy_func_details(original, value)
        return object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in _all_magics and name in self.__class__.__dict__:
            delattr(self.__class__, name)
        return object.__delattr__(self, name)
        
    def assert_called_with(self, *args, **kwargs):
        assert self.call_args == (args, kwargs), 'Expected: %s\nCalled with: %s' % ((args, kwargs), self.call_args)
        

def _dot_lookup(thing, comp, import_path):
    try:
        return getattr(thing, comp)
    except AttributeError:
        __import__(import_path)
        return getattr(thing, comp)


def _importer(target):
    components = target.split('.')
    import_path = components.pop(0)
    thing = __import__(import_path)

    for comp in components:
        import_path += ".%s" % comp
        thing = _dot_lookup(thing, comp, import_path)
    return thing


class _patch(object):
    def __init__(self, target, attribute, new, spec, create, mocksignature):
        self.target = target
        self.attribute = attribute
        self.new = new
        self.spec = spec
        self.create = create
        self.has_local = False
        self.mocksignature = False


    def __call__(self, func):
        if hasattr(func, 'patchings'):
            func.patchings.append(self)
            return func

        def patched(*args, **keywargs):
            # don't use a with here (backwards compatability with 2.5)
            extra_args = []
            for patching in patched.patchings:
                arg = patching.__enter__()
                if patching.new is DEFAULT:
                    extra_args.append(arg)
            args += tuple(extra_args)
            try:
                return func(*args, **keywargs)
            finally:
                for patching in getattr(patched, 'patchings', []):
                    patching.__exit__()

        patched.patchings = [self]
        patched.__name__ = func.__name__ 
        patched.compat_co_firstlineno = getattr(func, "compat_co_firstlineno", 
                                                func.func_code.co_firstlineno)
        return patched


    def get_original(self):
        target = self.target
        name = self.attribute
        create = self.create
        
        original = DEFAULT
        if _has_local_attr(target, name):
            try:
                original = target.__dict__[name]
            except AttributeError:
                # for instances of classes with slots, they have no __dict__
                original = getattr(target, name)
        elif not create and not hasattr(target, name):
            raise AttributeError("%s does not have the attribute %r" % (target, name))
        return original

    
    def __enter__(self):
        new, spec, = self.new, self.spec
        original = self.get_original()
        if new is DEFAULT:
            # XXXX what if original is DEFAULT - shouldn't use it as a spec
            inherit = False
            if spec == True:
                # set spec to the object we are replacing
                spec = original
                if isinstance(spec, (type, ClassType)):
                    inherit = True
            new = Mock(spec=spec)
            if inherit:
                new.return_value = Mock(spec=spec)
        new_attr = new
        if self.mocksignature:
            new_attr = mocksignature(original, new)
            
        self.temp_original = original
        setattr(self.target, self.attribute, new_attr)
        return new


    def __exit__(self, *_):
        if self.temp_original is not DEFAULT:
            setattr(self.target, self.attribute, self.temp_original)
        else:
            delattr(self.target, self.attribute)
        del self.temp_original
            
                
def patch_object(target, attribute, new=DEFAULT, spec=None, create=False, mocksignature=False):
    return _patch(target, attribute, new, spec, create, mocksignature)


def patch(target, new=DEFAULT, spec=None, create=False, mocksignature=False):
    try:
        target, attribute = target.rsplit('.', 1)    
    except (TypeError, ValueError):
        raise TypeError("Need a valid target to patch. You supplied: %r" % (target,))
    target = _importer(target)
    return _patch(target, attribute, new, spec, create, mocksignature)


def _has_local_attr(obj, name):
    try:
        return name in vars(obj)
    except TypeError:
        # objects without a __dict__
        return hasattr(obj, name)


magic_methods = (
    "lt le gt ge eq ne "
    "getitem setitem delitem "
    "len contains iter "
    "hash repr str unicode "
    "nonzero "
    "divmod neg pos abs invert "
    "complex int long float oct hex index "
)

numerics = "add sub mul div truediv floordiv mod lshift rshift and xor or "
inplace = ' '.join('i%s' % n for n in numerics.split())
right = ' '.join('r%s' % n for n in numerics.split()) 

def get_method(name, func):
    def method(self, *args, **kw):
        return func(self, *args, **kw)
    method.__name__ = name
    return method

_all_magics = set('__%s__' % method for method in ' '.join([magic_methods, numerics, inplace, right]).split())
