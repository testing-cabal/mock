# mock.py
# Test tools for mocking and patching.
# Copyright (C) 2007-2008 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk

# mock 0.5.0
# http://www.voidspace.org.uk/python/mock.html

# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/python/license.shtml

# Scripts maintained at http://www.voidspace.org.uk/python/index.shtml
# Comments, suggestions and bug reports welcome.

__all__ = (
    'Mock',
    'MakeMock',
    'patch',
    'patch_object',
    'sentinel',
    '__version__'
)

__version__ = '0.5.0 alpha'

DEFAULT = object()


class Mock(object):
    
    def __new__(cls, methods=None, spec=None, *args, **kwargs):
        if spec is not None or methods is not None:
            if methods is None:
                magics = [method for method in magic_methods if hasattr(spec, '__%s__' % method)]
            else:
                magics = [method[2:-2] for method in methods if ('__%s__' % method[2:-2] == method  and
                                                                 method[2:-2] in magic_methods)]
            if magics:
                # It might be magic, but I like it
                cls = MakeMock(magics)
        return object.__new__(cls)
        
    
    def __init__(self, methods=None, spec=None, side_effect=None, 
                 return_value=DEFAULT, name=None, parent=None,
                 items=None):
        self._parent = parent
        self._name = name
        if spec is not None and methods is None:
            methods = [member for member in dir(spec) if not 
                       (member.startswith('__') and  member.endswith('__'))]
        self._methods = methods
        self._children = {}
        self._return_value = return_value
        self.side_effect = side_effect
        
        if self._has_items():
            if items is None:
                items = {}
            self._items = items
        
        self.reset()

        
    def reset(self):
        self.called = False
        self.call_args = None
        self.call_count = 0
        self.call_args_list = []
        self.method_calls = []
        for child in self._children.itervalues():
            child.reset()
        if isinstance(self._return_value, Mock):
            self._return_value.reset()
    
            
    def _has_items(self):
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
            
        return self.return_value
    
    
    def __getattr__(self, name):
        if name == '__length_hint__':
            # an unfortunate workaround for mocking iterables
            raise AttributeError('__length_hint__')
        if self._methods is not None and name not in self._methods:
            raise AttributeError("object has no attribute '%s'" % name)
        
        if name not in self._children:
            self._children[name] = Mock(parent=self, name=name)
            
        return self._children[name]
    
    
    def assert_called_with(self, *args, **kwargs):
        assert self.call_args == (args, kwargs), 'Expected: %s\nCalled with: %s' % ((args, kwargs), self.call_args)
        

def _args(name, args=(), kwargs={}):
    return (name, args, kwargs)

def __getitem__(self, key):
    val = self._items[key]
    self.method_calls.append(_args('__getitem__', (key,)))
    return val
        
def __setitem__(self, key, value):
    self.method_calls.append(_args('__setitem__', (key, value)))
    self._items[key] = value
        
def __delitem__(self, key):
    self.method_calls.append(_args('__delitem__', (key,)))
    del self._items[key]

def __iter__(self):
    self.method_calls.append(_args('__iter__'))
    for item in list(self._items):
        yield item
        
def __len__(self):
    self.method_calls.append(_args('__len__'))
    return len(self._items)

def __contains__(self, key):
    self.method_calls.append(_args('__contains__'))
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

container_methods = ['nonzero', 'contains', 'len', 'setitem', 'iter', 'getitem', 'delitem']


def MakeMock(members):
    class MagicMock(Mock):
        def _has_items(self):
            return True
    
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


def _patch(target, attribute, new, methods, spec):
        
    def patcher(func):
        original = getattr(target, attribute)
        if hasattr(func, 'restore_list'):
            func.restore_list.append((target, attribute, original))
            func.patch_list.append((target, attribute, new, methods, spec))
            return func
        
        patch_list = [(target, attribute, new, methods, spec)]
        restore_list = [(target, attribute, original)]
        
        def patched(*args, **keywargs):
            for target, attribute, new, methods, spec in patch_list:
                if new is DEFAULT:
                    new = Mock(methods=methods, spec=spec)
                    args += (new,)
                setattr(target, attribute, new)
            try:
                return func(*args, **keywargs)
            finally:
                for target, attribute, original in restore_list:
                    setattr(target, attribute, original)
                    
        patched.restore_list = restore_list
        patched.patch_list = patch_list
        patched.__name__ = func.__name__ 
        patched.compat_co_firstlineno = getattr(func, "compat_co_firstlineno", 
                                                func.func_code.co_firstlineno)
        return patched
    
    return patcher


def patch_object(target, attribute, new=DEFAULT, methods=None, spec=None):
    return _patch(target, attribute, new, methods, spec)


def patch(target, new=DEFAULT, methods=None, spec=None):
    print target
    try:
        target, attribute = target.rsplit('.', 1)    
    except (TypeError, ValueError):
        raise TypeError("Need a valid target to patch. You supplied: %s" % (target,))
    target = _importer(target)
    return _patch(target, attribute, new, methods, spec)


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
