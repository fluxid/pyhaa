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
from . import matchers


def plexer_raise(eidd):
    def do_raise(parser):
        raise PyhaaSyntaxError(eidd, parser)
    return do_raise

def plexer_pass(parser):
    pass

def next_line(parser):
    if parser.body_started:
        return 'line'
    return 'head'


pyhaa_lexer = dict(
    _begin = 'head',

    # BASICS
    head = dict(
        match = (
            'head_statement_start',
            'line',
        ),
    ),
    line = dict(
        match = (
            'line_end', # Basically an empty line
            'indent',
        ),
    ),
    indent = dict(
        match = MRE('[ \t]*'),
        after = 'element',
    ),
    element = dict(
        match = (
            'escape',
            'comment',
            'tag',
            'code_statement_start',
            'code_expression_start',
            'html_raw_toggle',
            'constant',
            'text',
        ),
    ),
    continue_inline = dict(
        match = (
            'line_end',
            'inline',
        ),
    ),
    inline = dict(
        match = MRE('\s+'),
        after = 'element',
    ),
    line_end = dict(
        match = MRE('\s*$'),
        after = next_line,
    ),

    # HEAD statements
    head_statement_start = dict(
        match = MS('`'),
        after = 'head_statement',
    ),
    head_statement = dict(
        match = (
            'head_inherit',
            'head_partial',
        ),
    ),
    head_inherit = dict(
        match = matchers.MSS('inherit'),
        after = 'head_inherit_expression',
    ),
    head_inherit_expression = dict(
        match = matchers.PythonExpressionListMatcher(),
        after = 'line_end',
    ),
    head_partial = dict(
        match = matchers.MSS('def'),
        after = 'head_partial_name',
    ),
    head_partial_name = dict(
        match = matchers.PI(),
        after = 'head_partial_left_paren',
    ),
    head_partial_left_paren = dict(
        match = MRE('\s*\('),
        after = 'head_partial_parameters',
    ),
    head_partial_parameters = dict(
        match = matchers.PythonParameterListMatcher(),
        after = 'head_partial_right_paren',
    ),
    head_partial_right_paren = dict(
        match = MS('):'),
        after = 'line_end',
    ),

    # SMALL stuff
    escape = dict(
        match = MRE('\\\\\s*'),
        after = 'text',
    ),
    text = dict(
        match = MRE('(?P<value>.+?)[ \t]*$'),
        after = 'line_end',
    ),
    html_raw_toggle = dict(
        match = MRE('\?\s*'),
        after = 'element',
    ),
    comment = dict(
        match = MRE(';\s*(?P<comment>[^\s]*)\s*$'),
        after = 'line',
    ),
    constant = dict(
        match = MRE('!(?P<key>[^\s]+)'),
        after = 'line_end',
    ),

    # TAG stuff
    tag = dict(
        match = (
            'tag_name_start',
            'tag_class_start',
            'tag_id_start',
        ),
    ),
    tag_continue = dict(
        match = (
            'tag_class_start',
            'tag_id_start',
            'tag_after',
        ),
    ),

    tag_name_start = dict(
        match = MS('%'),
        after = 'tag_name',
    ),
    tag_name = dict(
        match = MRE('[^\.\#\(\{\s]*'), # Star - there may be no tag name - div by default
        after = 'tag_continue',
    ),

    tag_class_start = dict(
        match = MS('.'),
        after = 'tag_class_name',
    ),
    tag_class_name = dict(
        match = MRE('[^\.\#\(\{\s]+'),
        after = 'tag_continue',
        on_fail = plexer_raise(SYNTAX_INFO.EXPECTED_CLASSNAME),
    ),

    tag_id_start = dict(
        match = MS('#'),
        after = 'tag_id_name',
    ),
    tag_id_name = dict(
        match = MRE('[^\.\#\(\{\s]+'),
        after = 'tag_continue',
        on_fail = plexer_raise(SYNTAX_INFO.EXPECTED_IDNAME),
    ),

    # TAG ATTRIBUTES stuff
    tag_attributes = dict(
        match = (
            'tas_start', # tas - short for tag_attributes_simple
            'tap_start', # tap - short for tag_attributes_python
        ),
    ),
    tag_after = dict(
        match = (
            'tag_attributes',
            'continue_inline',
        ),
    ),

    # TAS - Tag Attributes Simple
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
        after = 'tag_after',
    ),
    tas_line_end = dict(
        match = MRE('\s*$'),
        after = 'tas_inside',
    ),

    # TAP - Tag Attributes Python
    tap_start = dict(
        match = matchers.ConstantLength(MS('{'), 0),
        after = 'tap_content',
        on_fail = plexer_pass,
    ),
    tap_content = dict(
        match = matchers.PythonDictMatcher(),
        after = 'tag_after',
    ),

    # PYTHON CODE stuff
    code_statement_start = dict(
        match = MRE('\-\s*'),
        after = 'code_statement_content',
    ),
    code_statement_content = dict(
        match = (
            'code_statement_expression',
            'code_statement_for',
            'code_statement',
            'code_statement_simple',
        ),
    ),

    # Statements including simple expression before colon
    code_statement_expression = dict(
        match = MM(
            matchers.PK('if'),
            matchers.PK('elif'),
            matchers.PK('while'),
        ),
        after = 'code_statement_expression_content',
    ),
    code_statement_expression_content = dict(
        match = matchers.PythonExpressionMatcher(break_at_colon=True),
        after = 'code_colon',
    ),

    # for..in statement
    code_statement_for = dict(
        match = matchers.PK('for'),
        after = 'code_statement_for_target',
    ),
    code_statement_for_target = dict(
        match = matchers.PythonTargetMatcher(),
        after = 'code_statement_for_in',
    ),
    code_statement_for_in = dict(
        match = matchers.PK('in', True),
        after = 'code_statement_for_expression',
    ),
    code_statement_for_expression = dict(
        match = matchers.PythonExpressionListMatcher(break_at_colon=True),
        after = 'code_colon',
    ),

    # Simple compound statements: name and colon immediately after it
    code_statement = dict(
        match = MM(
            # We allow only else at this moment, at least for now
            matchers.PK('else'),
        ),
        after = 'code_colon',
    ),

    # Colon always after a compund statement
    code_colon = dict(
        match = MRE('\s*:'),
        after = 'after_code_colon',
    ),
    after_code_colon = dict(
        match = (
            'line_end',
            'continue_inline',
        ),
    ),

    # Any simple statement, including normal expressions
    code_statement_simple = dict(
        match = matchers.PythonStatementMatcher(),
        after = 'line_end',
    ),

    # Expression which returns value to be inserted into template
    code_expression_start = dict(
        match = MRE('\=\s*'),
        after = 'code_expression',
    ),
    code_expression = dict(
        match = matchers.PythonExpressionMatcher(),
        after = 'line_end',
    ),
)

