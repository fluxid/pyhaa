# -*- coding: utf-8 -*-

'''
Testing parsing of invalid pyhaa code
Check if for given code are raised correct errors
'''

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
from unittest import TestCase
from warnings import catch_warnings

from pyhaa import (
    parse_string,
    PyhaaSyntaxError,
    PyhaaSyntaxWarning,
    SYNTAX_INFO,
)

from .helpers import jl

log = logging.getLogger(__name__)

class TestErrors(TestCase):
    def assertPSE(self, _eid, _func, *args, **kwargs):
        '''
        PSE is short of PythonSyntaxException... It is too long
        '''
        try:
            _func(*args, **kwargs)
        except PyhaaSyntaxError as e:
            log.debug('Got exception: %s', str(e) )
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
                '\t%',
                '  %',
                ' %',
            ),
        )
        self.assertEqual(exc.kwargs['width'], 2)

    def test_tab_width_2(self):
        exc = self.assertPSE(
            SYNTAX_INFO.INCONSISTENT_TAB_WIDTH,
            parse_string,
            jl(
                '%',
                '\t%',
                '  %',
                '   %',
            ),
        )
        self.assertEqual(exc.kwargs['width'], 2)

    def test_too_deep_indent(self):
        exc = self.assertPSE(
            SYNTAX_INFO.TOO_DEEP_INDENT,
            parse_string,
            jl(
                '%',
                ' %',
                ' %',
                '   %',
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
                    '\t%',
                    '%',
                    '\t\t %',
                ),
            )
        # Also, test if we were warned about spaces and tabs
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
                '\t%',
                '\t\t%',
                ' %',
            ),
        )

    def test_unexpected_indent_1(self):
        self.assertPSE(
            SYNTAX_INFO.UNEXPECTED_INDENT,
            parse_string,
            '\t%',
        )

    def test_unexpected_indent_2(self):
        self.assertPSE(
            SYNTAX_INFO.UNEXPECTED_INDENT,
            parse_string,
            jl(
                '%',
                '\ttext',
                '\t\tmore text',
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

    def test_id_already_set(self):
        self.assertPSE(
            SYNTAX_INFO.ID_ALREADY_SET,
            parse_string,
            '#s#d',
        )

