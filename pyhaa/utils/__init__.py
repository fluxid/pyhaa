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

import codecs
from contextlib import contextmanager
from functools import wraps
from itertools import count
import re

RE_DECAMEL = re.compile('[A-Z]')
RE_CAMEL = re.compile('^([a-z])|_([a-z])')
RE_CODING = re.compile(b'coding[:=]\s*([-\w.]+)')

# IMPORTANT: utf32 must go first because BOM_UTF32_LE starts with BOM_UTF16_LE!
# Otherwise we would detect UTF32 as UTF16 with two nullchars at the begining
BOMS = (
    (codecs.BOM_UTF8, 'utf-8'),
    (codecs.BOM_UTF32_BE, 'utf-32be'),
    (codecs.BOM_UTF32_LE, 'utf-32le'),
    (codecs.BOM_UTF16_BE, 'utf-16be'),
    (codecs.BOM_UTF16_LE, 'utf-16le'),
)

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

def one_iter(value):
    yield value

def iter_flatten(generator):
    iter_stack = list()
    current_iter = generator
    while True:
        try:
            result = next(current_iter)
        except StopIteration:
            if not iter_stack:
                break
            current_iter = iter_stack.pop()
            continue

        if hasattr(result, '__next__'):
            iter_stack.append(current_iter)
            current_iter = result
            continue

        yield result

def _decamel(match):
    return '_' + match.group(0).lower()

def decamel(string):
    # We're not removing '_' prefix
    return RE_DECAMEL.sub(_decamel, string)

def _camel(match):
    return (match.group(2) or match.group(1)).upper()

def camel(string):
    return RE_CAMEL.sub(_camel, string)

def try_detect_encoding(fp):
    '''
    Tries to detect file encoding, using BOM or coding-comment in
    similar way as Python does - with exception that we look only
    in the first line, since templates don't allow shebangs.

    Assumes current reading position is at the beginning of the file.
    '''
    # TODO: if both fails, how about trying chardet?
    line = fp.readline()
    for bom, encoding in BOMS:
        if line.startswith(bom):
            fp.seek(len(bom))
            return encoding

    fp.seek(0)

    match = RE_CODING.search(line)
    if not match:
        return None

    return match.group(1).decode('ascii')
        
