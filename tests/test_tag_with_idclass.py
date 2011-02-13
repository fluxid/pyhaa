# -*- coding: utf-8 -*-

'''
Testing tags with set class and/or id 
'''

from unittest import TestCase

from pyhaa import (
    parse_string,
)

from .helpers import jl


class TestTagsWithIdClass(TestCase):
    def test_only_class(self):
        tree = parse_string(jl(
            '.foo',
        ))
        tag, = tree.children
        self.assertSetEqual(tag.classes, {'foo'})

    def test_only_id(self):
        tree = parse_string(jl(
            '#bar',
        ))
        tag, = tree.children
        self.assertEqual(tag.id_, 'bar')

    def test_only_name(self):
        tree = parse_string(jl(
            '%div',
        ))
        tag, = tree.children
        self.assertEqual(tag.name, 'div')
        self.assertSetEqual(tag.classes, set())
        self.assertIs(tag.id_, None)

    def test_all_at_once(self):
        tree = parse_string(jl(
            '%div#head.rainbow.unicorns.autoclear',
        ))
        tag, = tree.children
        self.assertEqual(tag.name, 'div')
        self.assertSetEqual(tag.classes, {'rainbow', 'unicorns', 'autoclear'})
        self.assertEqual(tag.id_, 'head')

    def test_nested(self):
        tree = parse_string(jl(
            '%ul',
            '  %li spam',
            '  %li eggs',
        ))
        tag_ul, = tree.children
        self.assertEqual(tag_ul.name, 'ul')
        tag_li1, tag_li2 = tag_ul.children
        self.assertEqual(tag_li1.name, 'li')
        self.assertEqual(tag_li2.name, 'li')
        text1, = tag_li1.children
        text2, = tag_li2.children
        self.assertEqual(text1.text, 'spam')
        self.assertEqual(text2.text, 'eggs')

    def test_even_more_complicated(self):
        tree = parse_string(jl(
            '%ul#left_menu.socool',
            '  %li#first_one',
            '    %a.bling my pets',
            '  %li.pink %a.bounce my sweet photos',
        ))
        tag_ul, = tree.children
        self.assertEqual(tag_ul.name, 'ul')
        self.assertEqual(tag_ul.id_, 'left_menu')
        self.assertSetEqual(tag_ul.classes, {'socool'})
        tag_li1, tag_li2 = tag_ul.children
        self.assertEqual(tag_li1.name, 'li')
        self.assertEqual(tag_li2.name, 'li')
        self.assertEqual(tag_li1.id_, 'first_one')
        self.assertSetEqual(tag_li2.classes, {'pink'})
        tag_a1, = tag_li1.children
        tag_a2, = tag_li2.children
        self.assertSetEqual(tag_a1.classes, {'bling'})
        self.assertSetEqual(tag_a2.classes, {'bounce'})
        text1, = tag_a1.children
        text2, = tag_a2.children
        self.assertEqual(text1.text, 'my pets')
        self.assertEqual(text2.text, 'my sweet photos')

