import inspect
from mock import Mock

__all__ = ('mocksignature', 'MagicMock')

"""
extendmock adds additional features to the mock module.

The mocksignature function creates wrapper functions that call a mock whilst
preserving the signature of the original function.

Note that when a function signature is mocked with mocksignature it will *always* be
called with positional arguments and not keyword arguments (except where it
collects arguments with \*\*). Defaults will explicitly be supplied where the function
is called with missing arguments (as normal).

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

def getsignature(func):
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


def mocksignature(func, mock):
    signature = getsignature(func)
    src = "lambda %(signature)s: _mock_(%(signature)s)" % {'signature': signature}
    
    funcopy = eval(src, dict(_mock_=mock))
    funcopy.__name__ = func.__name__
    funcopy.__doc__ = func.__doc__
    funcopy.__dict__.update(func.__dict__)
    funcopy.__module__ = func.__module__
    funcopy.func_defaults = func.func_defaults
    return funcopy


class MagicMock(Mock):
    def __new__(cls, *args, **kw):
        class MagicMock(cls):
            # every instance has its own class
            # so we can create magic methods on the
            # class without stomping on other mocks
            pass
        return Mock.__new__(MagicMock, *args, **kw)

    def __setattr__(self, name, value):
        if name in _all_magics:
            method = _all_magics[name]
            setattr(self.__class__, name, method)
        return Mock.__setattr__(self, name, value)
    
    def __delattr__(self, name):
        if name in _all_magics and name in self.__class__.__dict__:
            delattr(self.__class__, name)
        return Mock.__delattr__(self, name)


magic_methods = (
    "lt le gt ge eq ne "
    "getitem setitem delitem "
    "len contains iter "
    "hash repr str "
    "nonzero "
    "divmod neg pos abs invert "
    "complex int long float oct hex index "
)

numerics = "add sub mul div truediv floordiv mod lshift rshift and xor or "
inplace = ' '.join('i%s' % n for n in numerics.split())
right = ' '.join('r%s' % n for n in numerics.split())


def get_method(name):
    def func(self, *args, **kw):
        return self.__dict__[name](self, *args, **kw)
    func.__name__ = name
    return func

_all_magics = {}
for method in sum([methods.split() for methods in [magic_methods, numerics, inplace, right]], []):
    name = '__%s__' % method 
    _all_magics[name] = get_method(name)
    
