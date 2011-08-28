# -*- coding: utf-8 -*-

'''
Testing tags with set class and/or id 
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

from .helpers import jl, PyhaaTestCase


class TestTagsWithIdClass(PyhaaTestCase):
    def test_only_class(self):
        tree = self.senv.parse_string(jl(
            '.foo',
        )).tree
        tag, = tree.children
        self.assertSetEqual(tag.classes, {'foo'})

    def test_only_id(self):
        tree = self.senv.parse_string(jl(
            '#bar',
        )).tree
        tag, = tree.children
        self.assertEqual(tag.id_, 'bar')

    def test_only_name(self):
        tree = self.senv.parse_string(jl(
            '%div',
        )).tree
        tag, = tree.children
        self.assertEqual(tag.name, 'div')
        self.assertSetEqual(tag.classes, set())
        self.assertIs(tag.id_, None)

    def test_all_at_once(self):
        tree = self.senv.parse_string(jl(
            '%div#head.rainbow.unicorns.autoclear',
        )).tree
        tag, = tree.children
        self.assertEqual(tag.name, 'div')
        self.assertSetEqual(tag.classes, {'rainbow', 'unicorns', 'autoclear'})
        self.assertEqual(tag.id_, 'head')

    def test_nested(self):
        tree = self.senv.parse_string(jl(
            '%ul',
            '  %li spam',
            '  %li eggs',
        )).tree
        tag_ul, = tree.children
        self.assertEqual(tag_ul.name, 'ul')
        tag_li1, tag_li2 = tag_ul.children
        self.assertEqual(tag_li1.name, 'li')
        self.assertEqual(tag_li2.name, 'li')
        text1, = tag_li1.children
        text2, = tag_li2.children
        self.assertEqual(text1.content, 'spam')
        self.assertEqual(text2.content, 'eggs')

    def test_even_more_complicated(self):
        # Random structure made for lolz
        tree = self.senv.parse_string(jl(
            '%ul#left_menu.socool',
            '  %li#first_one',
            '    %a.bling my pets',
            '  %li.pink %a.bounce my sweet photos',
        )).tree
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
        self.assertEqual(text1.content, 'my pets')
        self.assertEqual(text2.content, 'my sweet photos')

    def test_child_class(self):
        # Make sure we really called end_tag and 'foo' class wont be assigned
        # to previous tag
        tree = self.senv.parse_string(jl(
            '%',
            '  .foo',
        )).tree
        tag1, = tree.children
        tag2, = tag1.children
        self.assertSetEqual(tag1.classes, set())
        self.assertSetEqual(tag2.classes, {'foo'})

    def test_child_id(self):
        tree = self.senv.parse_string(jl(
            '%',
            '  #foo',
        )).tree
        tag1, = tree.children
        tag2, = tag1.children
        self.assertIs(tag1.id_, None)
        self.assertEqual(tag2.id_, 'foo')

    def test_child_class_inline(self):
        tree = self.senv.parse_string(jl(
            '% .foo',
        )).tree
        tag1, = tree.children
        tag2, = tag1.children
        self.assertSetEqual(tag1.classes, set())
        self.assertSetEqual(tag2.classes, {'foo'})

    def test_child_id_inline(self):
        tree = self.senv.parse_string(jl(
            '% #foo',
        )).tree
        tag1, = tree.children
        tag2, = tag1.children
        self.assertIs(tag1.id_, None)
        self.assertEqual(tag2.id_, 'foo')

