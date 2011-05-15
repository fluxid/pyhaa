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
    parse_string,
)
from pyhaa.codegen.html import HTMLCodeGen
from pyhaa.utils import iter_flatten

from .helpers import jl

class TestCodegenHtml(TestCase):
    def test_basic_codegen(self):
        tree = parse_string(jl(
            '%a',
        ))
        bio = io.BytesIO()
        cg = HTMLCodeGen(tree, bio, template_name = 'basic_template')
        cg.write()
        code = bio.getvalue().decode('utf-8')
        dict_ = dict()
        exec(code, dict_, dict_)
        template = dict_[dict_['template_class_name']]

    def test_html_encode_toggle_and_text(self):
        tree = parse_string(jl(
            '&',
            '?&',
            '?&amp;',
            '&amp;',
        ))
        bio = io.BytesIO()
        cg = HTMLCodeGen(tree, bio)
        cg.write()
        code = bio.getvalue()
        dict_ = dict()
        exec(code, dict_, dict_)
        template = dict_[dict_['template_class_name']]
        rendered = b''.join(iter_flatten(template().body(None))).decode('utf-8')
        self.assertEqual(
            rendered,
            '&amp; & &amp; &amp;',
        )

    def test_template_charset(self):
        tree = parse_string(jl(
            'Zażółć gęślą jaźń',
        ))
        bio = io.BytesIO()
        cg = HTMLCodeGen(tree, bio, encoding='iso-8859-2')
        cg.write()
        code = bio.getvalue()
        dict_ = dict()
        exec(code, dict_, dict_)
        template = dict_[dict_['template_class_name']]
        rendered = b''.join(iter_flatten(template().body(None))).decode('iso-8859-2')
        self.assertEqual(
            rendered,
            'Zażółć gęślą jaźń',
        )

    def test_expressions(self):
        tree = parse_string(jl(
            '=context[0]',
            '?=context[1]',
        ))
        bio = io.BytesIO()
        cg = HTMLCodeGen(tree, bio)
        cg.write()
        code = bio.getvalue()
        dict_ = dict()
        exec(code, dict_, dict_)
        template = dict_[dict_['template_class_name']]
        rendered = b''.join(iter_flatten(template().body(('&', '&amp;')))).decode('utf-8')
        self.assertEqual(
            rendered,
            '&amp;&amp;',
        )

