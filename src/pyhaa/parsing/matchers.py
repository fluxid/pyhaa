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

from fxd.minilexer import Matcher

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

class PythonBracketMatcher(Matcher):
    bracket = None

    def match(self, parser, line, pos):
        assert self.bracket in L_BRACKETS

        # We already matched left bracket, so
        # we need to add it to the beginning
        line = self.bracket + line[pos:]
        # and take pos one char back...
        pos -= 1

        readline = FakeByteReadline((line.encode('utf8'),))
        stack = list()
        ecol = 0

        try:
            for token in tokenize.tokenize(readline):
                ttype, tstring, (srow, scol), (erow, ecol), tline = token
                if srow == 0:
                    continue

                if ttype == tokenize.OP:
                    if tstring in L_BRACKETS:
                        stack.append(PAIRED_BRACKETS[tstring])
                    elif tstring in R_BRACKETS and tstring != stack.pop():
                        raise PyhaaSyntaxError(
                            SYNTAX_INFO.UNBALANCED_BRACKETS,
                            parser,
                            dict(current_pos = pos + scol),
                        )
                if not stack:
                    break
        except tokenize.TokenError:
            # Ignore. Let ast parse it again, actual error may be different
            pass

        line = line[:ecol]
        line2 = line.encode('utf8') + b'\n'

        with clear_exception_context(PyhaaSyntaxError):
            try:
                ast_tree = ast.parse(line2)
            except SyntaxError as e:
                # Offset is for bytes, not string characters
                # Even if I give normal string to parse, I'll get invalid
                # offset if line has unicode characters before it
                fragment = line2[:e.offset].decode('utf8')
                # substract 1 because python parser counts from one, and we
                # count from zero
                offset = len(fragment) - 1
                raise PyhaaSyntaxError(
                    SYNTAX_INFO.PYTHON_SYNTAX_ERROR,
                    parser,
                    dict(current_pos = pos + offset),
                    desc = e.msg,
                )

        self.check_ast(parser, line, pos, ast_tree)

        result = line
        if RE_EMPTY_BRACKETS[self.bracket].match(result):
            result = self.bracket + PAIRED_BRACKETS[self.bracket]

        # Substract length of left bracket
        return len(line)-1, result

    def check_ast(self, parser, ast_tree):
        pass


class PythonDictMatcher(PythonBracketMatcher):
    bracket = '{'

    def check_ast(self, parser, line, pos, ast_tree):
        if not isinstance(ast_tree.body[0].value, (ast.Dict, ast.DictComp)):
            raise PyhaaSyntaxError(
                SYNTAX_INFO.INVALID_PYTHON_ATTRIBUTES,
                parser,
                dict(
                    current_pos = pos,
                    length=len(line),
                ),
            )

