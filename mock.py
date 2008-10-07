# mock.py
# Test tools for mocking and patching.
# Copyright (C) 2007-2008 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk

# mock 0.4.0
# http://www.voidspace.org.uk/python/mock.html

# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/python/license.shtml

# Scripts maintained at http://www.voidspace.org.uk/python/index.shtml
# Comments, suggestions and bug reports welcome.


__all__ = (
    'Mock',
    'patch',
    'sentinel',
    '__version__'
)

__version__ = '0.4.0'

_default_return_value = object()


class Mock(object):
    def __init__(self, methods=None, spec=None, name=None, parent=None):
        self._parent = parent
        self._name = name
        if spec is not None and methods is None:
            methods = [member for member in dir(spec) if not 
                       (member.startswith('__') and  member.endswith('__'))]
        self._methods = methods
        self.reset()
        
        
    def reset(self):
        self.called = False
        self._return_value = _default_return_value
        self.call_args = None
        self.call_count = 0
        self.call_args_list = []
        self.method_calls = []
        self._children = {}
        
    
    def __get_return_value(self):
        if self._return_value == _default_return_value:
            self._return_value = Mock()
        return self._return_value
    
    def __set_return_value(self, value):
        self._return_value = value
        
    return_value = property(__get_return_value, __set_return_value)


    def __call__(self, *args, **keywargs):
        self.called = True
        self.call_count += 1
        self.call_args = (args, keywargs)
        self.call_args_list.append((args, keywargs))
        
        parent = self._parent
        name = self._name
        while parent is not None:
            parent.method_calls.append((name, args, keywargs))
            if parent._parent is None:
                break
            name = parent._name + '.' + name
            parent = parent._parent
        
        return self.return_value
    
    
    def __getattr__(self, name):
        if self._methods is not None and name not in self._methods:
            raise AttributeError("object has no attribute '%s'" % name)
        
        if name not in self._children:
            self._children[name] = Mock(parent=self, name=name)
            
        return self._children[name]
    
    
    def assert_called_with(self, *args, **kwargs):
        assert self.call_args == (args, kwargs), 'Called with %s' % (self.call_args,)
        

def _importer(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def patch(target, attribute, new=None):
    if isinstance(target, basestring):
        target = _importer(target)
        
    def patcher(func):
        original = getattr(target, attribute)
        if hasattr(func, 'restore_list'):
            func.restore_list.append((target, attribute, original))
            func.patch_list.append((target, attribute, new))
            return func
        
        func.restore_list = [(target, attribute, original)]
        func.patch_list = [(target, attribute, new)]
        
        def patched(*args, **keywargs):
            for target, attribute, new in func.patch_list:
                if new is None:
                    new = Mock()
                    args += (new,)
                setattr(target, attribute, new)
            try:
                return func(*args, **keywargs)
            finally:
                for target, attribute, original in func.restore_list:
                    setattr(target, attribute, original)
                    
        patched.__name__ = func.__name__ 
        return patched
    
    return patcher


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
