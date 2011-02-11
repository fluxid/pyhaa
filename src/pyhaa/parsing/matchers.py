# -*- coding: utf-8 -*-

import ast
import tokenize

from fxd.minilexer import Matcher

from .errors import PyhaaSyntaxError

from ..utils import (
    clear_exception_context,
    FakeByteReadline,
)

L_BRACKETS = ('{', '(', '[')
R_BRACKETS = ('}', ')', ']')
PAIRED_BRACKETS = dict(zip(L_BRACKETS, R_BRACKETS))


class PythonBracketMatcher(Matcher):
    bracket = None

    def match(self, context, line, pos):
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
                            context,
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
                result = ast.parse(line2)
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
                    context,
                    dict(current_pos = pos + offset),
                    desc = e.msg,
                )

        self.check_ast(result)
        # Substract length of {
        return len(line)-1, line

    def check_ast(self, ast_tree):
        pass


class PythonDictMatcher(PythonBracketMatcher):
    bracket = '{'

    def check_ast(self, ast_tree):
        if not isinstance(ast_tree.body[0].value, (ast.Dict, ast.DictComp)):
            raise PyhaaSyntaxError(
                SYNTAX_INFO.INVALID_PYTHON_ATTRIBUTES,
                context,
                dict(
                    current_pos = pos,
                    length=len(line),
                ),
            )

