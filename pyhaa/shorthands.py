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

__all__ = (
    'codegen_template',
    'compile_template',
    'html_render_to_iterator',
    'html_render_to_string',
    'parse_io',
    'parse_readline',
    'parse_string',
)

def parse_readline(readline, parser_class=PyhaaParser):
    parser = parser_class()
    parser.parse_readline(readline)
    parser.finish()
    return parser.tree

def parse_io(fileobj):
    return parse_readline(fileobj.readline)

def parse_string(string):
    return parse_io(io.StringIO(string))

def codegen_template(tree, codegen_class = HTMLCodeGen, **kwargs):
    bio = io.BytesIO()
    cg = codegen_class(tree, bio, **kwargs)
    cg.write()
    return bio.getvalue()

def compile_template(code):
    dict_ = dict()
    exec(code, dict_, dict_)
    template = dict_[dict_['template_class_name']]
    return template

def html_render_to_iterator(template, function_name=None, args=None, kwargs=None):
    if isinstance(template, type):
        template = template()
    args = args or list()
    kwargs = kwargs or dict()
    function = getattr(template, function_name or 'body')
    iterator = function(*args, **kwargs)
    return iterator

def html_render_to_string(template, *args, **kwargs):
    with decapsulate_exceptions():
        iterator = html_render_to_iterator(template, *args, **kwargs)
        rendered = b''.join(iter_flatten(iterator)).decode(template.encoding)
        return rendered

