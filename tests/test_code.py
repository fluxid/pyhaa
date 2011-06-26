# -*- coding: utf-8 -*-

'''
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

from unittest import TestCase

from pyhaa import (
    parse_string,
    structure,
)

from .helpers import jl

class TestCode(TestCase):
    def test_basic_expressions(self):
        tree = parse_string(jl(
            '%placeholder',
            '=a()',
            '= "b"',
            '%placeholder2',
        )).tree
        tag1, code1, code2, tag2 = tree
        self.assert_(isinstance(tag1, structure.Tag))
        self.assert_(isinstance(code1, structure.Expression))
        self.assert_(isinstance(code2, structure.Expression))
        self.assert_(isinstance(tag2, structure.Tag))

    def test_multiline_expressions(self):
        # Testing nasty multiline expressions with bad indenting
        tree = parse_string(jl(
            '=c((',
            '      d',
            'for d in e',
            '))',
            '="g" \\',
            '"h"   ;',
            '= i(',
            '  {  ',
            ' "a": "b"',
            '}, 2',
            '   )  ',
        )).tree
        code1, code2, code3 = tree
        self.assert_(isinstance(code1, structure.Expression))
        self.assert_(isinstance(code2, structure.Expression))
        self.assert_(isinstance(code3, structure.Expression))

    def test_if_elif_while_statements(self):
        tree = parse_string(jl(
            '-if(1): %tag',
            '-elif True:',
            '  %tag',
            '-while \tFalse:',
            '  Will not happen!',
        )).tree
        s1, s2, s3 = tree
        t1, = s1
        t2, = s2
        t3, = s3
        self.assert_(isinstance(s1, structure.CompoundStatement))
        self.assert_(isinstance(s2, structure.CompoundStatement))
        self.assert_(isinstance(s3, structure.CompoundStatement))
        self.assert_(isinstance(t1, structure.Tag))
        self.assert_(isinstance(t2, structure.Tag))
        self.assert_(isinstance(t3, structure.Text))
        self.assertEqual(s1.content, 'if (1):')
        self.assertEqual(s2.content, 'elif True:')
        self.assertEqual(s3.content, 'while False:')
        self.assertEqual(s1.name, 'if')
        self.assertEqual(s2.name, 'elif')
        self.assertEqual(s3.name, 'while')

    def test_else_statements(self):
        tree = parse_string(jl(
            '-else \t  : %tag',
            '-else:',
            '  sup!',
        )).tree
        s1, s2 = tree
        t1, = s1
        t2, = s2
        self.assert_(isinstance(s1, structure.CompoundStatement))
        self.assert_(isinstance(s2, structure.CompoundStatement))
        self.assert_(isinstance(t1, structure.Tag))
        self.assert_(isinstance(t2, structure.Text))
        self.assertEqual(s1.content, 'else:')
        self.assertEqual(s2.content, 'else:')
        self.assertEqual(s1.name, 'else')
        self.assertEqual(s2.name, 'else')

    def test_for_statement(self):
        tree = parse_string(jl(
            '-for a in range(10): %tag',
            '-for(a)in(range(10)) :',
            '  sup!',
        )).tree
        s1, s2 = tree
        t1, = s1
        t2, = s2
        self.assert_(isinstance(s1, structure.CompoundStatement))
        self.assert_(isinstance(s2, structure.CompoundStatement))
        self.assert_(isinstance(t1, structure.Tag))
        self.assert_(isinstance(t2, structure.Text))
        self.assertEqual(s1.content, 'for a in range(10):')
        self.assertEqual(s2.content, 'for (a) in (range(10)):')
        self.assertEqual(s1.name, 'for')
        self.assertEqual(s2.name, 'for')

    def test_simple_statement_name(self):
        tree = parse_string(jl(
            '-return(1)',
            '-break',
            '-assert False \t ',
        )).tree
        s1, s2, s3 = tree
        self.assert_(isinstance(s1, structure.SimpleStatement))
        self.assert_(isinstance(s2, structure.SimpleStatement))
        self.assert_(isinstance(s3, structure.SimpleStatement))
        self.assertEqual(s1.name, 'return')
        self.assertEqual(s2.name, 'break')
        self.assertEqual(s3.name, 'assert')

