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

from io import StringIO
#import logging

from .lexer import pyhaa_lexer
from .parser import PyhaaParser

__all__ = (
    'parse_io',
    'parse_readline',
    'parse_string',
)

#log = logging.getLogger(__name__)


def parse_readline(readline):
    parser = PyhaaParser()
    parser.parse_readline(readline)
    parser.finish()
    return parser.tree

def parse_io(fileobj):
    return parse_readline(fileobj.readline)

def parse_string(string):
    return parse_io(StringIO(string))
