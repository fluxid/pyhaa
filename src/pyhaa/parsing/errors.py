# -*- coding: utf-8 -*-

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
    ('UNBALANCED_BRACKETS', 'Unbalanced brackets in Python expression.'),
    ('PYTHON_SYNTAX_ERROR', 'Python syntax error: "{desc}".'),
    ('INVALID_PYTHON_ATTRIBUTES', (
        'Pythonic attributes must be dictionary or '
        'dictionary comprehension literal.'
    )),
)

log = logging.getLogger(__name__)


class PyhaaSyntaxInfo:
    def __init__(self, _eidd, _context, _overwrite=None, **kwargs):
        if isinstance(_eidd, int):
            eid = _eidd
            description = SYNTAX_INFO.get_desc(eid)
        else:
            eid = None
            description = _eidd

        self.eid = eid
        self.description = description
        self.context = _context
        self.overwrite = _overwrite
        self.kwargs = kwargs
        super().__init__()

    def _get_value(self, name):
        value = None
        if self.overwrite:
            value = self.overwrite.get(name)
        if value is None:
            value = getattr(self.context, name)
        return value

    @log_error(log)
    def __str__(self):
        description = self.description.format(**self.kwargs)

        c = self.context
        # Show actual state of indent level
        indent = '[{}]'.format(self._get_value('indent'))
        # Strip indent
        iline = self._get_value('current_line').rstrip()
        line = iline.lstrip()
        indent_length = len(iline) - len(line)

        pos = self._get_value('current_pos') - indent_length
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
            self._get_value('current_lineno'),
            description,
            indent,
            line,
            ' ' * len(indent),
            '-' * pos,
            '^' * (self._get_value('length') or 1),
        )


class PyhaaSyntaxError(PyhaaSyntaxInfo, Exception):
    pass


class PyhaaSyntaxWarning(PyhaaSyntaxInfo, UserWarning):
    pass


def warn_syntax(*args, **kwargs):
    # I don't care about stack level here,
    # warning is about pyhaa code anyay.
    warnings.warn(PyhaaSyntaxWarning(*args, **kwargs))

