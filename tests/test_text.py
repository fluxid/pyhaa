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

from pyhaa import (
    parse_string,
)

from pyhaa.structure import (
    Tag,
    Text,
)

from .helpers import jl, PyhaaTestCase

class TestText(PyhaaTestCase):
    def test_text(self):
        tree = parse_string(jl(
            'spam and eggs',
        )).tree
        text1 = tree.children[0]
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.content, 'spam and eggs')

    def test_escape(self):
        tree = parse_string(jl(
            '\\%i am no tag!',
        )).tree
        text1 = tree.children[0]
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.content, '%i am no tag!')

    def test_inline_text(self):
        tree = parse_string(jl(
            '%some-tag.class#id %child text',
        )).tree
        tmp = tree
        tmp, = tmp.children # unpack tree children
        tmp, = tmp.children # unpack first child children
        tmp, = tmp.children # etc
        text1 = tmp
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.content, 'text')

    def test_inline_escape(self):
        tree = parse_string(jl(
            '%some-tag.class#id %child \\%text',
        )).tree
        tmp = tree
        tmp, = tmp.children # unpack tree children
        tmp, = tmp.children # unpack first child children
        tmp, = tmp.children # etc
        text1 = tmp
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.content, '%text')

    def test_noninline_text(self):
        tree = parse_string(jl(
            '%some-tag.class#id',
            '  %child',
            '    text',
        )).tree
        tmp = tree
        tmp, = tmp.children # unpack tree children
        tmp, = tmp.children # unpack first child children
        tmp, = tmp.children # etc
        text1 = tmp
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.content, 'text')

    def test_noninline_escape(self):
        tree = parse_string(jl(
            '%some-tag.class#id',
            '  %child',
            '    \\%text',
        )).tree
        tmp = tree
        tmp, = tmp.children # unpack tree children
        tmp, = tmp.children # unpack first child children
        tmp, = tmp.children # etc
        text1 = tmp
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.content, '%text')

    def test_joining(self):
        tree = parse_string(jl(
            'foo',
            '\%',
            'bar',
        )).tree
        text1, = tree
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.content, 'foo % bar')

    def test_stripped(self):
        tree = parse_string(jl(
            '\  \t  foo   \t  ',
            'bar  \t  ',
        )).tree
        text1, = tree
        self.assertTrue(isinstance(text1, Text))
        self.assertEqual(text1.content, 'foo bar')

    def test_escape_toggle(self):
        tree = parse_string(jl(
            '&amp;',
            '?&amp;',
            '?&amp;',
            '&amp;',
        )).tree
        text1, text2, text3 = tree
        self.assertEqual(text1.escape, True)
        self.assertEqual(text2.escape, False)
        self.assertEqual(text3.escape, True)
        self.assertEqual(text1.content, '&')
        self.assertEqual(text2.content, '&amp; &amp;')
        self.assertEqual(text3.content, '&')

    def test_constant(self):
        tree = parse_string(jl(
            '!html5',
            '!sp',
        )).tree
        text1, text2 = tree
        self.assertEqual(text1.escape, False)
        self.assertEqual(text2.escape, True)
        self.assertEqual(text1.content, '<!DOCTYPE html>')
        self.assertEqual(text2.content, ' ')

    def test_comment(self):
        # Best place for this test...
        tree = parse_string(jl(
            'test2',
            ';',
            '; ',
            '%',
            '  ;a',
            '  Text',
            ';a',
            '; a',
            ';a ',
            '; a ',
            ';',
            'test2',
        )).tree
        t1, t2, t3 = tree
        t4, = t2
        self.assertTrue(isinstance(t1, Text))
        self.assertTrue(isinstance(t2, Tag))
        self.assertTrue(isinstance(t3, Text))
        self.assertTrue(isinstance(t4, Text))

