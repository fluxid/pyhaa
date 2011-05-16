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

import logging
import warnings

from ..utils import (
    DescEnum,
    log_error,
)

__all__ = (
    'SYNTAX_INFO',
    'PyhaaSyntaxError',
    'PyhaaSyntaxWarning',
)

SYNTAX_INFO = DescEnum(
    ('SYNTAX_ERROR', "Syntax error - lexer couldn't match any token."),
    ('EXPECTED_CLASSNAME', 'Expected class name'),
    ('EXPECTED_IDNAME', 'Expected id name'),
    ('INCONSISTENT_TAB_WIDTH', (
        'Inconsistent tab width. Found {tabs} tabs and {spaces} spaces. '
        'Earlier detected tab width is {width}, current indent is {indent}.'
    )),
    ('TOO_DEEP_INDENT', (
        'To deep indent. Current indent is {indent}, attepted to '
        'change it to {new_indent}'
    )),
    ('INVALID_INDENT', (
        'Invalid indent. Found {tabs} tabs and {spaces} spaces. '
        'No tab width was detected, current indent is {indent}.'
    )),
    ('INDENT_TAB_SPACES', (
        "Using tabs ({tabs}) and spaces ({spaces}) in one line at once. I'll "
        "try to continue but this may fail."
    )),
    ('UNEXPECTED_INDENT', 'Unexpected indent'),
    ('EXPECTED_INDENT', 'Expected indent'),
    ('UNBALANCED_BRACKETS', 'Unbalanced brackets in Python expression.'),
    ('PYTHON_SYNTAX_ERROR', 'Python syntax error: "{desc}".'),
    ('INVALID_PYTHON_ATTRIBUTES', (
        'Pythonic attributes must be dictionary or '
        'dictionary comprehension literal.'
    )),
    ('INVALID_PYTHON_EXPRESSION', "Invalid python expression."),
    ('ID_ALREADY_SET', "Tag's id is already set."),
)

log = logging.getLogger(__name__)


class PyhaaSyntaxInfo:
    def __init__(self, _eidd, _parser, _overwrite=None, **kwargs):
        if isinstance(_eidd, int):
            eid = _eidd
            description = SYNTAX_INFO.get_desc(eid)
        else:
            eid = None
            description = _eidd

        self.eid = eid
        self.description = description
        self.parser = _parser
        self.overwrite = _overwrite
        self.kwargs = kwargs
        super().__init__()

    def get_value(self, name):
        value = None
        if self.overwrite:
            value = self.overwrite.get(name)
        if value is None:
            value = getattr(self.parser, name)
        return value

    @log_error(log)
    def __str__(self):
        description = self.description.format(**self.kwargs)

        # Show actual state of indent level
        indent = '[{}]'.format(self.get_value('indent'))
        # Strip indent
        iline = self.get_value('current_line').rstrip()
        line = iline.lstrip()
        indent_length = len(iline) - len(line)

        pos = self.get_value('current_pos') - indent_length
        # We start 'dashline' one character earlier.
        # If position is negative, it's problem with indent. Set it
        # to zero so ^ appears one character before start of line
        pos += 1
        if pos < 0:
            pos = 0

        return (
            'At line {}: {}\n'
            '{} {}\n'
            '{}{}{}'
        ).format(
            self.get_value('current_lineno'),
            description,
            indent,
            line,
            ' ' * len(indent),
            '-' * pos,
            '^' * (self.get_value('length') or 1),
        )


class PyhaaSyntaxError(PyhaaSyntaxInfo, Exception):
    pass


class PyhaaSyntaxWarning(PyhaaSyntaxInfo, UserWarning):
    pass


def warn_syntax(*args, **kwargs):
    # I don't care about stack level here,
    # warning is about pyhaa code anyay.
    warnings.warn(PyhaaSyntaxWarning(*args, **kwargs))

