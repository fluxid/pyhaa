# -*- coding: utf-8 -*-

from io import StringIO
#import logging

from fxd.minilexer import parse

from .lexer import pyhaa_lexer

__all__ = (
    'parse_io',
    'parse_readline',
    'parse_string',
)

#log = logging.getLogger(__name__)


def parse_readline(readline):
    context = parse(pyhaa_lexer, readline)
    #return context.tree

def parse_io(fileobj):
    return parse_readline(fileobj.readline)

def parse_string(string):
    return parse_io(StringIO(string))
