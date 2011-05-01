# -*- coding: utf-8 -*-

# Pyhaa - Templating system for Python 3
# Copyright (c) 2011 Tomasz Kowalczyk
# Contact e-mail: code@fluxid.pl
#
# This library is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
# 
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this library in the file COPYING.LESSER. If not, see
# <http://www.gnu.org/licenses/>.

from contextlib import contextmanager
from functools import wraps
from itertools import count
import re

# TODO
# I don't have access to internet now so I won't list all entities here
ENTITIES_DECODE = {
    'amp': '&',
    'quot': '"',
    'apos': "'",
    'lt': '<',
    'gt': '>',
}
RE_ENTITIES_ENCODE = re.compile('&([^\s;&]+);')

_ENCODEABLE = '&\'"<>'
_ENTITIES_ENCODE = {
    value: key
    for key, value in ENTITIES_DECODE.items()
}
ENTITIES_ENCODE = {
    character: (
        '&#{};'.format(ord(character))
        if entity is None else
        '&{};'.format(entity)
    )
    for character, entity in (
        (character, _ENTITIES_ENCODE.get(character))
        for character in _ENCODEABLE
    )
}
del _ENTITIES_ENCODE, _ENCODEABLE


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
    Clears explicitly exception context, so "The above exception was the direct
    cause of the following exception:" does not appear.
    '''
    if not etypes:
        etypes = Exception
    try:
        yield
    except etypes as e:
        e.__context__ = None
        raise


def dict_sub(dict_, regex=None, group_id=None):
    if not regex:
        regex = re.compile('[' + re.escape(''.join(dict_.keys())) + ']')
        group_id = 0

    def match_sub(match):
        match = match.group(group_id)
        return dict_.get(match, match)

    def replacer(value, *args, **kwargs):
        return regex.sub(match_sub, value, *args, **kwargs)

    return replacer


entity_decode = dict_sub(ENTITIES_DECODE, RE_ENTITIES_ENCODE, 1)


entity_encode = dict_sub(ENTITIES_ENCODE)


