import inspect
from mock import Mock

__all__ = ('mocksignature', 'MagicMock')

"""
extendmock adds additional features to the mock module.

The mocksignature function creates wrapper functions that call a mock whilst
preserving the signature of the original function.

MagicMock is a class that adds magic method support to Mock. You add magic methods
to mock instances in the same way you mock other attributes::

    mock = Mock()
    mock.__repr__ = lambda self: 'some string'

Note that functions (or callable objects like a Mock instance) that are used for 
magic methods must take self as the first argument.
 
The only unsupported magic methods (that I'm aware of) are:

* Used by Mock: __init__, __new__, __getattr__, __setattr__, __delattr__
* Rare: __dir__,
* Can cause bad interactions with other functionality: 

    - __reversed__, __missing__, __del__, __unicode__, __getattribute__
    - __get__, __set__, __delete__

* Context manager methods are not directly supported (__enter__ and __exit__) as
  Python doesn't lookup these methods on the class as it should (in Python 2.5 / 2.6
  anyway).

For more examples of how to use mocksignature and MagicMock see the tests.
"""

# getsignature and mocksignature heavily "inspired" by
# the decorator module: http://pypi.python.org/pypi/decorator/
# by Michele Simionato

DELEGATE = MISSING = object()

def getsignature(func, handle_defaults=False):
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

magic_methods = [
    ("lt le gt ge eq ne", NotImplemented),
    ("getitem setitem delitem", TypeError),
    ("len contains iter", TypeError),
    ("hash repr str", DELEGATE),
    ("nonzero", True),
    ("divmod neg pos abs invert", TypeError),
    ("complex int long float oct hex index", TypeError)
]

numerics = "add sub mul div truediv floordiv mod lshift rshift and xor or"
inplace = ' '.join('i%s' % n for n in numerics.split())
right = ' '.join('r%s' % n for n in numerics.split())

magic_methods.extend([
    (numerics, NotImplemented), (inplace, NotImplemented), (right, NotImplemented)
])

def get_method(name, action):
    def func(self, *args, **kw):
        real = self.__dict__.get(name, MISSING)
        if real is not MISSING:
            return real(self, *args, **kw)
        if action is NotImplemented:
            return NotImplemented   
        elif isinstance(action, type) and issubclass(action, Exception):
            raise action
        elif action is DELEGATE:
            return getattr(Mock, name)(self, *args, **kw)
        return action
    func.__name__ = name
    return func
    
for methods, action in magic_methods:
    for method in methods.split():
        name = '__%s__' % method
        setattr(MagicMock, name, get_method(name, action))
    
    