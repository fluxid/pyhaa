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

import ast
import re
import tokenize

from fxd.minilexer import (
    Matcher,
    MRE,
)

from .errors import (
    PyhaaSyntaxError,
    SYNTAX_INFO,
)

from ..utils import (
    clear_exception_context,
    FakeByteReadline,
)

L_BRACKETS = ('{', '(', '[')
R_BRACKETS = ('}', ')', ']')
PAIRED_BRACKETS = dict(zip(L_BRACKETS, R_BRACKETS))

RE_EMPTY_BRACKETS = {
    left: re.compile('^{}[ \t\n\r\f\v]*{}$'.format(re.escape(left), re.escape(right)), re.M)
    for left, right in PAIRED_BRACKETS.items()
}


class ConstantLength(Matcher):
    def __init__(self, orig, length):
        self.orig = orig
        self.length = length
        super().__init__()

    def match(self, parser, line, pos):
        result = self.orig.match(parser, line, pos)
        if result is not None:
            _, result = result
            return pos + self.length, result
        return None
        

class PythonStatementMatcher(Matcher):
    match_bracket = None
    should_check_ast = True
    break_at_colon = False
    break_at_keyword = []
    break_at_unknown_bracket = False

    def __init__(self, break_at_colon = None, break_at_keyword = None):
        if not break_at_keyword is None:
            self.break_at_keyword = break_at_keyword

        if not break_at_colon is None:
            self.break_at_colon = break_at_colon

    def match(self, parser, line, pos):
        parser.cache_push()

        # We're not interested in what was before
        line = line[pos:]
        if self.match_bracket:
            assert self.match_bracket in L_BRACKETS and line[0] == self.match_bracket
        lines = []

        def linegen():
            yield line
            while True:
                yield parser.readline()
        lineiter = linegen()
        
        def readline():
            current_line = next(lineiter, '')
            lines.append(current_line)
            return current_line.encode('utf8')

        stack = list()
        erow = 1
        ecol = 0

        try:

            for token in tokenize.tokenize(readline):
                ttype, tstring, (srow, scol), (erow, ecol), tline = token
                if not srow:
                    continue

                if ttype in (tokenize.NEWLINE, tokenize.ENDMARKER):
                    break

                if ttype == tokenize.OP:
                    if tstring in L_BRACKETS:
                        stack.append(PAIRED_BRACKETS[tstring])
                    elif tstring in R_BRACKETS:
                        if not stack and self.break_at_unknown_bracket:
                            # Remove matched braket from line
                            ecol -= 1
                            break

                        if not stack or tstring != stack.pop():
                            raise PyhaaSyntaxError(
                                SYNTAX_INFO.UNBALANCED_BRACKETS,
                                parser,
                                dict(current_pos = pos + scol),
                            )
                    elif self.break_at_colon and tstring == ':' and not stack:
                        # Get back one char, so ast won't whine about
                        # syntax error caused by colon
                        ecol -= 1
                        break

                elif ttype == tokenize.NAME and not stack and tstring in self.break_at_keyword:
                    ecol -= len(tstring)
                    break

                if self.match_bracket and not stack:
                    break

        except tokenize.TokenError:
            if not self.should_check_ast:
                raise
            # Ignore. Let ast parse it again, actual error may be different

        lines = lines[:srow]
        lines[-1] = lines[-1][:ecol].rstrip()

        # FIXME Tokenizer reads a bit ahead... Deal with it better than below
        parser.cache_pop()
        for i in range(len(lines)-1):
            parser.readline()

        jlines = ''.join(lines)

        if self.should_check_ast:
            jlines2 = (jlines+'\n').encode('utf8')
            context = self.get_context(line)
            subtract = 0
            if context:
                jlines2 = context[0] + jlines2 + context[1]
                subtract = len(context[0])
            with clear_exception_context(PyhaaSyntaxError):
                try:
                    ast_tree = ast.parse(jlines2)
                except SyntaxError as e:
                    # Offset is for bytes, not string characters
                    # Even if I give normal string to parse, I'll get invalid
                    # offset if line has unicode characters before it
                    fragment = jlines2[:e.offset].decode('utf8')
                    # subtract 1 because python parser counts from one, and we
                    # count from zero
                    # We also subtract length of context code prepended to line
                    # Use max for case if context code is messed up
                    offset = max(len(fragment) - 1 - subtract, 0)
                    raise PyhaaSyntaxError(
                        SYNTAX_INFO.PYTHON_SYNTAX_ERROR,
                        parser,
                        dict(current_pos = pos + offset),
                        desc = e.msg,
                    )

            self.check_ast(parser, line, pos, ast_tree)

        if self.match_bracket:
            if RE_EMPTY_BRACKETS[self.match_bracket].match(jlines):
                jlines = self.match_bracket + PAIRED_BRACKETS[self.match_bracket]

        if len(lines) > 1:
            pos = 0

        return pos + len(lines[-1]), jlines

    def check_ast(self, parser, line, pos, ast_tree):
        pass

    def get_context(self, line):
        '''
        This returns context code before and after matched fragment of code.
        It is needed for ast parser so we can check syntax for small parts
        of code in larger code (e.g. list of function attributes).
        Should return None or 2-tuple with bytes - code before and after to
        be added.
        '''
        return None


class PythonDictMatcher(PythonStatementMatcher):
    match_bracket = '{'

    def check_ast(self, parser, line, pos, ast_tree):
        if not isinstance(ast_tree.body[0].value, (ast.Dict, ast.DictComp)):
            raise PyhaaSyntaxError(
                SYNTAX_INFO.INVALID_PYTHON_ATTRIBUTES,
                parser,
            )


class PythonExpressionMatcher(PythonStatementMatcher):
    def check_ast(self, parser, line, pos, ast_tree):
        if not (len(ast_tree.body) == 1 and isinstance(ast_tree.body[0], ast.Expr)):
            raise PyhaaSyntaxError(
                SYNTAX_INFO.INVALID_PYTHON_EXPRESSION,
                parser,
            )


class PythonExpressionListMatcher(PythonStatementMatcher):
    def check_ast(self, parser, line, pos, ast_tree):
        if not (ast_tree.body and all(isinstance(item, ast.Expr) for item in ast_tree.body)):
            raise PyhaaSyntaxError(
                SYNTAX_INFO.INVALID_PYTHON_EXPRESSION,
                parser,
            )


class PythonTargetMatcher(PythonExpressionMatcher):
    break_at_keyword = ['in']

    def check_ast(self, parser, line, pos, ast_tree):
        super().check_ast(parser, line, pos, ast_tree)
        value = ast_tree.body[0].value
        if not isinstance(value, (ast.Attribute, ast.Tuple, ast.List, ast.Name, ast.Starred, ast.Subscript)):
            raise PyhaaSyntaxError(
                SYNTAX_INFO.INVALID_PYTHON_TARGET,
                parser,
            )


class PythonParameterListMatcher(PythonStatementMatcher):
    break_at_unknown_bracket = True

    def get_context(self, line):
        return (b'def noname(', b'): pass')


def PK(value, spaces=False):
    '''
    Python keyword matcher - basicaly w word and any amount of whitespace
    '''
    regex = r'({})\b\s*'
    if spaces:
        regex = r'\s*' + regex
    return MRE(regex.format(value))

def MSS(value):
    '''
    Match string and whiespace after it
    '''
    return MRE('{}\s+'.format(re.escape(value)))

class PI(MRE):
    '''
    Matches Python identifier
    '''
    def __init__(self):
        super().__init__('\w+')

    def match(self, *args, **kwargs):
        result = super().match(*args, **kwargs)
        if not result:
            return None
        idx, result = result
        result = result.group(0)
        if result.isidentifier():
            return idx, result
        return None

