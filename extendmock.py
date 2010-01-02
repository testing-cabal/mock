import inspect
from mock import Mock

__all__ = ('mocksignature', 'MagicMock')

def getsignature(func, handle_defaults=False):
    assert inspect.ismethod(func) or inspect.isfunction(func)
    regargs, varargs, varkwargs, defaults = inspect.getargspec(func)
    argnames = list(regargs)
    if varargs:
        argnames.append(varargs)
    if varkwargs:
        argnames.append(varkwargs)
    
    dd = {}
    if handle_defaults:
        dd[formatvalue] = lambda value: ""
    signature = inspect.formatargspec(regargs, varargs, varkwargs, defaults, **dd)
    return signature[1:-1]

def mocksignature(func, mock, handle_defaults=False):
    signature = getsignature(func, handle_defaults=handle_defaults)
    src = "lambda %(signature)s: _mock_(%(signature)s)" % {'signature': signature}
    funcopy = eval(src, dict(_mock_=mock))
    funcopy.__name__ = func.__name__
    funcopy.__doc__ = func.__doc__
    funcopy.__dict__.update(func.__dict__)
    funcopy.__module__ = func.__module__
    funcopy.func_defaults = func.func_defaults
    return funcopy

class MagicMock(Mock):
    pass

MISSING = object()

# Not supported: 
# Used by Mock: __init__, __new__, __getattr__, __setattr__, __delattr__
# Rare: __dir__,
# Can cause bad interactions with other functionality: 
#   __reversed__, __missing__, __del__, __unicode__, __getattribute__
#   __get__, __set__, __delete__

magic_methods = list((
    "eq ne lt le gt ge" 
    "nonzero hash getitem setitem delitem"
    "len contains iter repr str"
    "divmod neg pos abs invert"
    "complex int long float oct hex index"
    "enter exit"
).split())

numerics = "add sub mul div truediv floordiv mod lshift rshift and xor or".split()
magic_methods.extend(numerics)
magic_methods.extend('i%s' % m for m in numerics)
magic_methods.extend('r%s' % m for m in numerics)


def get_method(name):
    def func(self, *args, **kw):
        real = getattr(self, name, MISSING)
        if real is not MISSING:
            return real(self, *args, **kw)
        return getattr(Mock, name)(self, *args, **kw)
    func.__name__ = name
    return func
    
for method in magic_methods:
    name = '__%s__' % method
    setattr(MagicMock, name, get_method(name))
    
    