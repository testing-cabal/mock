# mock.py
# Test tools for mocking and patching.
# Copyright (C) 2007-2008 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk

# mock 0.5.0
# http://www.voidspace.org.uk/python/mock/

# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/python/license.shtml

# Scripts maintained at http://www.voidspace.org.uk/python/index.shtml
# Comments, suggestions and bug reports welcome.


__all__ = (
    'Mock',
    'MakeMock',
    'patch',
    'patch_object',
    'sentinel'
)

__version__ = '0.5.0 alpha'

DEFAULT = object()
class OldStyleClass:
    pass
ClassType = type(OldStyleClass)

def _is_magic(name):
    return '__%s__' % name[2:-2] == name

def _copy(value):
    if type(value) in (dict, list, tuple, set):
        return type(value)(value)
    return value

class Mock(object):
    
    def __new__(cls, spec=None, magics=None, *args, **kwargs):
        if isinstance(spec, list):           
            magics = [method[2:-2] for method in spec if (_is_magic(method) and method[2:-2] in magic_methods)]
        elif spec is not None:
            magics = [method for method in magic_methods if hasattr(spec, '__%s__' % method)]
        elif isinstance(magics, basestring):
            magics = magics.split()
            
        if magics:
            # It might be magic, but I like it
            cls = MakeMock(magics)
        return object.__new__(cls)
        
    
    def __init__(self, spec=None, magics=None, side_effect=None, 
                 return_value=DEFAULT, name=None, parent=None,
                 items=None, wraps=None):
        self._parent = parent
        self._name = name
        if spec is not None and not isinstance(spec, list):
            spec = [member for member in dir(spec) if not _is_magic(member)]
        
        self._methods = spec
        self._children = {}
        self._return_value = return_value
        self.side_effect = side_effect
        self._wraps = wraps
        
        self.__items = None
        self.reset_mock()
        
        if self._has_items():
            if items is None:
                items = {}
            self._items = items
            self.__items = _copy(items)

        
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
        if self._has_items():
            self._items = _copy(self.__items)
    
            
    def _has_items(self):
        # Overriden in MagicMock
        return False
        
    
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

        if self.side_effect is not None:
            self.side_effect()
            
        if self._wraps is not None:
            return self._wraps(*args, **kwargs)
        return self.return_value
    
    
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
    
    
    def assert_called_with(self, *args, **kwargs):
        assert self.call_args == (args, kwargs), 'Expected: %s\nCalled with: %s' % ((args, kwargs), self.call_args)
        

def _args(name, *args):
    return (name, args, {})

def __getitem__(self, key):
    val = self._items[key]
    self.method_calls.append(_args('__getitem__', key))
    return val
        
def __setitem__(self, key, value):
    self.method_calls.append(_args('__setitem__', key, value))
    self._items[key] = value
        
def __delitem__(self, key):
    self.method_calls.append(_args('__delitem__', key))
    del self._items[key]

def __iter__(self):
    self.method_calls.append(_args('__iter__'))
    for item in list(self._items):
        yield item
        
def __len__(self):
    self.method_calls.append(_args('__len__'))
    return len(self._items)

def __contains__(self, key):
    self.method_calls.append(_args('__contains__', key))
    return key in self._items

def __nonzero__(self):
    self.method_calls.append(_args('__nonzero__'))
    return bool(self._items)
    

magic_methods = {
    'delitem': __delitem__,
    'getitem': __getitem__,
    'setitem': __setitem__,
    'iter': __iter__,
    'len': __len__,
    'contains': __contains__,
    'nonzero': __nonzero__
}


def MakeMock(members):
    class MagicMock(Mock):
        def _has_items(self):
            return True
        
    if 'all' in members:
        members = magic_methods.keys()
    for method in members:
        if method not in magic_methods:
            raise NameError("Unknown magic method %r" % method)
        
        impl = magic_methods[method]
        name = '__%s__' % method
        setattr(MagicMock, name, impl)
    return MagicMock

        
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
    def __init__(self, target, attribute, new, spec, magics, create):
        self.target = target
        self.attribute = attribute
        self.new = new
        self.spec = spec
        self.magics = magics
        self.create = create


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
        try:
            return getattr(self.target, self.attribute)
        except AttributeError:
            if not self.create:
                raise
            return DEFAULT 


    def __enter__(self):
        new, spec, magics  = self.new, self.spec, self.magics
        original = self.get_original()
        if new is DEFAULT:
            inherit = False
            if spec == True:
                # set spec to the object we are replacing
                spec = original
                if isinstance(spec, (type, ClassType)):
                    inherit = True
            new = Mock(spec=spec, magics=magics)
            if inherit:
                # deliberately ignoring magics as we are using spec
                new.return_value = Mock(spec=spec)
        self.temp_original = original
        setattr(self.target, self.attribute, new)
        return new


    def __exit__(self, *_):
        if self.temp_original is not DEFAULT:
            setattr(self.target, self.attribute, self.temp_original)
        else:
            delattr(self.target, self.attribute)
        del self.temp_original
            
                

def patch_object(target, attribute, new=DEFAULT, spec=None, magics=None, create=False):
    return _patch(target, attribute, new, spec, magics, create)


def patch(target, new=DEFAULT, spec=None, magics=None, create=False):
    try:
        target, attribute = target.rsplit('.', 1)    
    except (TypeError, ValueError):
        raise TypeError("Need a valid target to patch. You supplied: %r" % (target,))
    target = _importer(target)
    return _patch(target, attribute, new, spec, magics, create)


class SentinelObject(object):
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return '<SentinelObject "%s">' % self.name


class Sentinel(object):
    def __init__(self):
        self._sentinels = {}
        
    def __getattr__(self, name):
        return self._sentinels.setdefault(name, SentinelObject(name))
    
    
sentinel = Sentinel()
