# -*- coding: utf-8 -*-

from contextlib import contextmanager
from functools import wraps
from itertools import count


class DescEnum:
    __slots__ = ('to_desc', 'to_name', 'to_value')

    def __init__(self, *args):
        counter = count()
        to_desc = dict()
        to_name = dict()
        to_value = dict()
        for name, desc in args:
            value = next(counter)
            to_desc[value] = desc
            to_name[value] = name
            to_value[name] = value

        self.to_desc = to_desc
        self.to_name = to_name
        self.to_value = to_value

    def get_desc(self, value):
        return self.to_desc[value]

    def get_name(self, value):
        return self.to_name[value]

    def __getattr__(self, name):
        value = self.to_value.get(name)
        if value is None:
            raise AttributeError(name)
        return value


class FakeByteReadline:
    '''
    Truns iterable into readline-style callable
    '''
    def __init__(self, args):
        self.lines = iter(args)

    def __call__(self):
        if self.lines is None:
            return b''
        line = next(self.lines, b'')
        if not line:
            self.lines = None
        elif not line.endswith(b'\n'):
            line += b'\n'
        return line


def log_error(log):
    '''
    Forces logging exception into given log.
    '''
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                log.exception(e)
                raise
        return wrapper
    return decorator


@contextmanager
def clear_exception_context(etypes = None):
    '''
    Clears explicitly exception context, so 'The above exception was the direct
    cause of the following exception:' does noe appear.
    '''
    if not etypes:
        etypes = Exception
    try:
        yield
    except etypes as e:
        e.__context__ = None
        raise

