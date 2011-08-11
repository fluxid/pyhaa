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

from pyhaa import (
    codegen,
    parse_string,
)

from .helpers import jl, PyhaaTestCase

class TestingCodeGen(codegen.CodeGen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.called_functions = list()

    def call_node_handling_function(self, prefix, node):
        self.called_functions.append(codegen.name_node_handling_function(prefix, node))


class TestCodegen(PyhaaTestCase):
    def test_basic_codegen(self):
        structure = parse_string(jl(
            '%a',
            '  %b',
            '%c',
            'text',
            '=expression',
            'again, text!',
            '?raw text',
            '?=raw_expression',
        ))
        bio = io.BytesIO()
        cg = TestingCodeGen(structure, bio)
        cg.write()
        bio.getvalue().decode('utf-8')
        self.assertSequenceEqual(
            cg.called_functions,
            [
                'handle_open_pyhaa_tree',
                'handle_open_tag',
                'handle_open_tag',
                'handle_close_tag',
                'handle_close_tag',
                'handle_open_tag',
                'handle_close_tag',
                'handle_open_text',
                'handle_close_text',
                'handle_open_expression',
                'handle_close_expression',
                'handle_open_text',
                'handle_close_text',
                'handle_open_text',
                'handle_close_text',
                'handle_open_expression',
                'handle_close_expression',
                'handle_close_pyhaa_tree',
            ],
        )

