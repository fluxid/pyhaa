# -*- coding: utf-8 -*-

'''
Testing partial stuff...
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

class TestPartials(TestCase):
    def test_basic_partial(self):
        structure = parse_string(jl(
            '`def hello(a, b, c):',
            '  %h1 partial',
            '  =a',
            '  =b',
            '  =c',
            '`def lol():',
            '  lol',
            '=self.hello("a", "b", "c")',
            '=self.lol()',
        ))
        self.assertEqual(len(structure.partials), 2)
        self.assertIn('hello', structure.partials)
        self.assertIn('lol', structure.partials)
        code1, code2 = structure.tree
        self.assert_(isinstance(code1, structure.Expression))
        self.assert_(isinstance(code2, structure.Expression))
        self.assertEqual(len(structure.partials['hello']), 4)
        self.assertEqual(len(structure.partials['lol']), 1)
        

