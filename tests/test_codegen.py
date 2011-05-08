# -*- coding: utf-8 -*-

'''
Test code generation
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

import io
from unittest import TestCase

from pyhaa import (
    codegen,
    parse_string,
)

from .helpers import jl

class TestCodeGen(codegen.CodeGen):
    def write_node(self, node):
        '''
        Don't throw exception, just pass
        '''
        pass

class TestBasics(TestCase):
    def test_basic_codegen(self):
        tree = parse_string(jl(
            '%a',
            '  %b',
            '%c',
        ))
        bio = io.BytesIO()
        cg = TestCodeGen(tree, bio)
        cg.write()
        bio.getvalue().decode('utf-8')

