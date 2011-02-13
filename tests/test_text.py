# -*- coding: utf-8 -*-

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

