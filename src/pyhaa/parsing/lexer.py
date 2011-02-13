# -*- coding: utf-8 -*-

from fxd.minilexer import (
    MM,
    MRE,
    MS,
)

from .context import PyhaaParsingContext
from .errors import PyhaaSyntaxError, SYNTAX_INFO
from .matchers import PythonDictMatcher


def plexer_raise(eidd):
    def do_raise(context):
        raise PyhaaSyntaxError(eidd, context)
    return do_raise

def plexer_pass(context):
    pass

pyhaa_lexer = dict(
    _context_class = PyhaaParsingContext,
    _begin = 'line',
    _on_bad_token = plexer_raise(SYNTAX_INFO.SYNTAX_ERROR),
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
            'escape',
            'text',
        ),
    ),
    escape = dict(
        match = MS('\\'),
        after = 'text',
    ),
    text = dict(
        match = MRE('.+$'),
        after = 'line_end',
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
            'tas_end'
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
    tap_start = dict(
        match = MS('{'),
        after = 'tap_rest',
        on_fail = plexer_pass,
    ),
    tap_rest = dict(
        match = PythonDictMatcher(),
        after = 'tag_after_attributes',
    ),
)
