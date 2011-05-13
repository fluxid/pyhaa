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

from fxd.minilexer import (
    MM,
    MRE,
    MS,
)

from .errors import PyhaaSyntaxError, SYNTAX_INFO
from .matchers import (
    ConstantLength,
    PythonDictMatcher,
)


def plexer_raise(eidd):
    def do_raise(parser):
        raise PyhaaSyntaxError(eidd, parser)
    return do_raise

def plexer_pass(parser):
    pass

pyhaa_lexer = dict(
    _begin = 'line',
    line = dict(
        match = (
            'line_end',
            'indent',
        ),
    ),
    indent = dict(
        match = MRE('[ \t]*'),
        after = 'element',
    ),
    element = dict(
        match = (
            'comment',
            'tag_start',
            'html_escape_toggle',
            'escape',
            'text',
        ),
    ),
    escape = dict(
        match = MRE('\\\\\s*'),
        after = 'text',
    ),
    text = dict(
        match = MRE('(?P<value>.+?)[ \t]*$'),
        after = 'line_end',
    ),
    html_escape_toggle = dict(
        match = MRE('\?\s*'),
        after = 'element',
    ),
    tag_start = dict(
        match = (
            'tag_name_start',
            'tag_class_start',
            'tag_id_start',
        ),
    ),
    tag_name_start = dict(
        match = MS('%'),
        after = 'tag_name',
    ),
    tag_name = dict(
        match = MRE('[^\.\#\(\{\s]*'),
        after = 'tag_options',
    ),
    tag_class_start = dict(
        match = MS('.'),
        after = 'tag_class_name',
    ),
    tag_class_name = dict(
        match = MRE('[^\.\#\(\{\s]+'),
        after = 'tag_options',
        on_fail = plexer_raise(SYNTAX_INFO.EXPECTED_CLASSNAME),
    ),
    tag_id_start = dict(
        match = MS('#'),
        after = 'tag_id_name',
    ),
    tag_id_name = dict(
        match = MRE('[^\.\#\(\{\s]+'),
        after = 'tag_options',
        on_fail = plexer_raise(SYNTAX_INFO.EXPECTED_IDNAME),
    ),
    tag_options = dict(
        match = (
            'tag_id_start',
            'tag_class_start',
            'tag_after_attributes',
        ),
    ),
    tag_after_attributes = dict(
        match = (
            'tag_attributes',
            #'spaceset',
            'line_end',
            'continue_inline',
        ),
    ),
    continue_inline = dict(
        match = MRE('\s+'),
        after = 'inline',
    ),
    inline = dict(
        match = (
            'element',
            'line_end',
        ),
    ),
    line_end = dict(
        match = MRE('\s*$'),
        after = 'line',
    ),
    comment = dict(
        match = MRE('!\s*(?P<comment>[^\s]*)\s*$'),
        after = 'line',
    ),
    tag_attributes = dict(
        match = (
            'tas_start', # tas - short for tag_attributes_simple
            'tap_start', # tap - short for tag_attributes_python
        ),
    ),
    tas_start = dict(
        match = MS('('),
        after = 'tas_inside',
        on_fail = plexer_pass,
    ),
    tas_inside = dict(
        match = (
            'tas_name',
            'tas_end',
            'tas_line_end',
        ),
    ),
    tas_name = dict(
        match = MRE('\s*(?P<value>[^\s\)\=]+)'),
        after = 'tas_name_after',
    ),
    tas_name_after = dict(
        match = (
            'tas_value',
            'tas_inside',
        ),
    ),
    tas_value = dict(
        match = MM(
            MRE('\s*=\s*\'(?P<value>[^\']*)\''),
            MRE('\s*=\s*\"(?P<value>[^\"]*)\"'),
            MRE('\s*=\s*(?P<value>[^\s\)]+)'),
        ),
        after = 'tas_inside',
    ),
    tas_end = dict(
        match = MRE('\s*\)'),
        after = 'tag_after_attributes',
    ),
    tas_line_end = dict(
        match = MRE('\s*$'),
        after = 'tas_inside',
    ),
    tap_start = dict(
        match = ConstantLength(MS('{'), 0),
        after = 'tap_rest',
        on_fail = plexer_pass,
    ),
    tap_rest = dict(
        match = PythonDictMatcher(),
        after = 'tag_after_attributes',
    ),
    #code_statement_start = dict(
    #    match = MRE('\-\s*'),
    #    after = 'code_statement',
    #),
    #code_statement = dict(
    #    match = MRE('.+?\s*$'),
    #    after = 'line_end',
    #),
    #code_value_start = dict(
    #    match = MRE('\=\s*'),
    #    after = 'code_value',
    #),
    #code_value = dict(
    #    match = MRE('.+?\s*$'),
    #    after = 'line_end',
    #),
)
