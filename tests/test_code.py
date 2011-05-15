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
)

from .helpers import jl

class TestBasicTags(TestCase):
    def test_basic_expressions(self):
        tree = parse_string(jl(
            '%placeholder',
            '=a()',
            '= "b"',
            '%placeholder2',
        ))
        #tag1, code1, code2, tag2 = tree
        #self.assertIsInstance(tag1, structure.Tag)
        #self.assertIsInstance(tag2, structure.Tag)

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
        ))

