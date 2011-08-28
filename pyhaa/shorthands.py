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

import io

from .codegen.html import HTMLCodeGen
from .parsing.lexer import pyhaa_lexer
from .parsing.parser import PyhaaParser
from .runtime import decapsulate_exceptions, EncapsulatedException
from .utils import iter_flatten

# TODO Scrap all of below and enforce usage of environment!

__all__ = (
    'html_render_to_iterator',
    'html_render_to_string',
)


def html_render_to_iterator(template, function_name=None, args=None, kwargs=None):
    if isinstance(template, type):
        # Aaargh
        template = template(None)
    args = args or list()
    kwargs = kwargs or dict()
    function = template
    if function_name:
        function = getattr(template, function_name or 'body')
    iterator = function(*args, **kwargs)
    return iterator

def html_render_to_string(template, *args, **kwargs):
    with decapsulate_exceptions():
        iterator = html_render_to_iterator(template, *args, **kwargs)
        rendered = b''.join(iter_flatten(iterator)).decode(template.encoding)
        return rendered

