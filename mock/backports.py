import sys


if sys.version_info[:2] < (3, 8):

    import functools
    from asyncio.coroutines import _is_coroutine
    from inspect import ismethod, isfunction, CO_COROUTINE

    def _unwrap_partial(func):
        while isinstance(func, functools.partial):
            func = func.func
        return func

    def _has_code_flag(f, flag):
        """Return true if ``f`` is a function (or a method or functools.partial
        wrapper wrapping a function) whose code object has the given ``flag``
        set in its flags."""
        while ismethod(f):
            f = f.__func__
        f = _unwrap_partial(f)
        if not isfunction(f):
            return False
        return bool(f.__code__.co_flags & flag)

    def iscoroutinefunction(obj):
        """Return true if the object is a coroutine function.

        Coroutine functions are defined with "async def" syntax.
        """
        return (
            _has_code_flag(obj, CO_COROUTINE) or
            getattr(obj, '_is_coroutine', None) is _is_coroutine
        )

else:

    from asyncio import iscoroutinefunction

