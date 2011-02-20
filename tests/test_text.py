# -*- coding: utf-8 -*-

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

from pyhaa.structure import (
    Text,
)

from .helpers import jl

class TestText(TestCase):
    def test_text(self):
        tree = parse_string(jl(
            'spam and eggs',
        ))
        text1 = tree.children[0]
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.text, 'spam and eggs')

    def test_escape(self):
        tree = parse_string(jl(
            '\\%i am no tag!',
        ))
        text1 = tree.children[0]
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.text, '%i am no tag!')

    def test_inline_text(self):
        tree = parse_string(jl(
            '%some-tag.class#id %child text',
        ))
        tmp = tree
        tmp, = tmp.children # unpack tree children
        tmp, = tmp.children # unpack first child children
        tmp, = tmp.children # etc
        text1 = tmp
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.text, 'text')

    def test_inline_escape(self):
        tree = parse_string(jl(
            '%some-tag.class#id %child \\%text',
        ))
        tmp = tree
        tmp, = tmp.children # unpack tree children
        tmp, = tmp.children # unpack first child children
        tmp, = tmp.children # etc
        text1 = tmp
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.text, '%text')

    def test_noninline_text(self):
        tree = parse_string(jl(
            '%some-tag.class#id',
            '  %child',
            '    text',
        ))
        tmp = tree
        tmp, = tmp.children # unpack tree children
        tmp, = tmp.children # unpack first child children
        tmp, = tmp.children # etc
        text1 = tmp
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.text, 'text')

    def test_noninline_escape(self):
        tree = parse_string(jl(
            '%some-tag.class#id',
            '  %child',
            '    \\%text',
        ))
        tmp = tree
        tmp, = tmp.children # unpack tree children
        tmp, = tmp.children # unpack first child children
        tmp, = tmp.children # etc
        text1 = tmp
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.text, '%text')

    def test_joining(self):
        tree = parse_string(jl(
            'foo',
            '\%',
            'bar',
        ))
        text1, = tree
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.text, 'foo % bar')

