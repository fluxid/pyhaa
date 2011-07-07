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
#from copy import copy
from sys import exc_info

class Template:
    def __init__(self, environment, parent = None):
        self.environment = environment
        self.parent = parent

class EncapsulatedException(Exception):
    '''
    This Exceptions "encapsulates" other exception so it won't be matched
    by try..except where we don't want it to be caught.
    '''
    def __init__(self, original):
        self.original = original
        super().__init__(original)

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            repr(self.original),
        )
    
    def __str__(self):
        return repr(self)

@contextmanager
def encapsulate_exceptions():
    '''
    We encapsulate exception mostly for case if this is StopIteration kind
    of error. When we iterate, we should only catch StopIteration only
    raised by generator itself, not by code inside it, so we use
    with statement to encapsulate exception raised inside generator,
    and then we reraise them in try..except clause "above" iterating code.
    '''
    try:
        yield
    except EncapsulatedException:
        # Ignore already encapsulated exception
        raise
    except Exception as exc:
        raise EncapsulatedException(exc).with_traceback(exc_info()[2])

class decapsulate_exceptions:
    '''
    Decapsulate exceptions processed by encapsulate_exceptions.
    This context manager is not based on contextlib.contextlib because
    we need to support raising StopIteration
    '''
    def __init__(self, pop_frames=2):
        self.pop_frames = pop_frames

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and issubclass(exc_type, EncapsulatedException):
            raise exc_val.original
        return False

