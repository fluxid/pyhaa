# -*- coding: utf-8 -*-

'''
Test HTML code generation
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
    codegen_template,
    compile_template,
    html_render_to_string,
    parse_string,
)

from .helpers import jl


class TestCodegenHtml(TestCase):
    def test_basic_codegen(self):
        tree = parse_string(jl(
            '%p',
            '  %a Text',
            '%input(checked)',
            '%div',
        ))
        code = codegen_template(tree, template_name = 'basic_template')
        template = compile_template(code)
        self.assertEqual(template.__name__, 'BasicTemplate')
        rendered = html_render_to_string(template, args=[None])
        self.assertEqual(
            rendered,
            '<p><a>Text</a></p><input checked="checked" /><div></div>',
        )

    def test_void_tags(self):
        tree = parse_string(jl(
            '%br Text',
        ))
        self.assertRaises(Exception, codegen_template, tree)

    def test_dynamic_tags(self):
        tree = parse_string(jl(
            '%p.a.b{"class": context[0], "_tag_name": context[1]}',
        ))
        code = codegen_template(tree)
        template = compile_template(code)
        rendered = html_render_to_string(template, args=[('c', 'div')])
        self.assertEqual(
            rendered,
            '<div class="c"></div>',
        )

    def test_html_encode_toggle_and_text(self):
        tree = parse_string(jl(
            '&',
            '?&',
            '?&amp;',
            '&amp;',
        ))
        code = codegen_template(tree)
        template = compile_template(code)
        rendered = html_render_to_string(template, args=[None])
        self.assertEqual(
            rendered,
            '&amp; & &amp; &amp;',
        )

    def test_template_charset(self):
        tree = parse_string(jl(
            'Zażółć gęślą jaźń',
        ))
        code = codegen_template(tree, encoding='iso-8859-2')
        template = compile_template(code)
        rendered = html_render_to_string(template, args=[None])
        self.assertEqual(
            rendered,
            'Zażółć gęślą jaźń',
        )

    def test_expressions(self):
        tree = parse_string(jl(
            '=context[0]',
            '?=context[1]',
        ))
        code = codegen_template(tree)
        template = compile_template(code)
        rendered = html_render_to_string(template, args=[('&', '&amp;')])
        self.assertEqual(
            rendered,
            '&amp;&amp;',
        )

    def test_while_if(self):
        tree = parse_string(jl(
            '-my_iter = iter(context)',
            '%ul',
            '  -while True:',
            '    -value = next(my_iter, None)',
            '    -if value is None:',
            '      -break',
            '    %li =value',
        ))
        code = codegen_template(tree)
        template = compile_template(code)
        rendered = html_render_to_string(template, args=[['1', '2', '3']])
        self.assertEqual(
            rendered,
            '<ul><li>1</li><li>2</li><li>3</li></ul>',
        )

    def test_for(self):
        tree = parse_string(jl(
            '%ul',
            '  -for value in context:',
            '    %li =value',
        ))
        code = codegen_template(tree)
        template = compile_template(code)
        rendered = html_render_to_string(template, args=[['1', '2', '3']])
        self.assertEqual(
            rendered,
            '<ul><li>1</li><li>2</li><li>3</li></ul>',
        )

    def test_for_inline(self):
        tree = parse_string(jl(
            '%ul -for value in context: %li =value',
        ))
        code = codegen_template(tree)
        template = compile_template(code)
        rendered = html_render_to_string(template, args=[['1', '2', '3']])
        self.assertEqual(
            rendered,
            '<ul><li>1</li><li>2</li><li>3</li></ul>',
        )

