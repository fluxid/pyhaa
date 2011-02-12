# -*- coding: utf-8 -*-

'''
Testing parsing of invalid pyhaa code
Check if for given code are raised correct errors
'''

from unittest import TestCase
from warnings import catch_warnings

from pyhaa import (
    parse_string,
    PyhaaSyntaxError,
    PyhaaSyntaxWarning,
    SYNTAX_INFO,
)

from .helpers import jl

class TestErrors(TestCase):
    def assertPSE(self, _eid, _func, *args, **kwargs):
        '''
        PSE is short of PythonSyntaxException... It is too long
        '''
        try:
            _func(*args, **kwargs)
        except PyhaaSyntaxError as e:
            self.assertEqual(e.eid, _eid)
            # We may want to check further details
            return e
        self.fail()

    def test_syntax_error(self):
        '''
        Test random syntax error.
        It won't cover all possible syntax errors, of course.
        '''
        self.assertPSE(
            SYNTAX_INFO.SYNTAX_ERROR,
            parse_string,
            '%}',
        )

    def test_classname(self):
        self.assertPSE(
            SYNTAX_INFO.EXPECTED_CLASSNAME,
            parse_string,
            '. text',
        )

    def test_idname(self):
        self.assertPSE(
            SYNTAX_INFO.EXPECTED_IDNAME,
            parse_string,
            '# text',
        )

    def test_tab_width_1(self):
        exc = self.assertPSE(
            SYNTAX_INFO.INCONSISTENT_TAB_WIDTH,
            parse_string,
            jl(
                '%',
                '\ttext',
                '  text',
                ' text',
            ),
        )
        self.assertEqual(exc.kwargs['width'], 2)

    def test_tab_width_2(self):
        exc = self.assertPSE(
            SYNTAX_INFO.INCONSISTENT_TAB_WIDTH,
            parse_string,
            jl(
                '%',
                '\ttext',
                '  text',
                '   text',
            ),
        )
        self.assertEqual(exc.kwargs['width'], 2)

    def test_too_deep_indent(self):
        exc = self.assertPSE(
            SYNTAX_INFO.TOO_DEEP_INDENT,
            parse_string,
            jl(
                '%',
                ' text',
                ' text',
                '   text',
            ),
        )
        self.assertEqual(exc.context.tab_width, 1)

    def test_invalid_indent_1(self):
        with catch_warnings(record=True) as warns:
            exc = self.assertPSE(
                SYNTAX_INFO.INVALID_INDENT,
                parse_string,
                jl(
                    '%',
                    '\ttext',
                    'text',
                    '\t\t text',
                ),
            )
        # Also, test if we're warned about spaces and tabs
        self.assertEqual(len(warns), 1)
        warning = warns[0].message
        self.assertTrue(isinstance(warning, PyhaaSyntaxWarning))
        self.assertEqual(warning.kwargs['spaces'], 1)
        self.assertEqual(warning.kwargs['tabs'], 2)

    def test_invalid_indent_2(self):
        self.assertPSE(
            SYNTAX_INFO.INVALID_INDENT,
            parse_string,
            jl(
                '%',
                '\ttext',
                '\t\ttext',
                ' text',
            ),
        )

    def test_unbalanced_brackets(self):
        self.assertPSE(
            SYNTAX_INFO.UNBALANCED_BRACKETS,
            parse_string,
            '%{)}',
        )

    def test_syntax_error(self):
        self.assertPSE(
            SYNTAX_INFO.PYTHON_SYNTAX_ERROR,
            parse_string,
            '%{;}',
        )

    def test_invalid_python_attributes(self):
        self.assertPSE(
            SYNTAX_INFO.INVALID_PYTHON_ATTRIBUTES,
            parse_string,
            '%{1}',
        )
