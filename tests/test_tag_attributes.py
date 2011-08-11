# -*- coding: utf-8 -*-

'''
Testing basic tag structures and pyhaa tree structure in general
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

from pyhaa import (
    parse_string,
)
from pyhaa.utils.cgrt_common import (
    prepare_for_tag as pft,
)

from .helpers import jl, PyhaaTestCase

class TestTagAttributes(PyhaaTestCase):
    def test_empty_attributes(self):
        tree = parse_string(jl(
            '%',
            '%(){}()',
            '%( \t     ){  \t  }',
        )).tree
        tag1, tag2, tag3 = tree.children
        self.assertAttributesEqual(tag1, {})
        self.assertAttributesEqual(tag2, {})
        self.assertAttributesEqual(tag3, {})

    def test_attributes_names(self):
        # Dirty style but still valid
        tree = parse_string(jl(
            '%(foo \t bar)',
            '%( \t baz\t \t)',
        )).tree
        tag1, tag2 = tree.children
        self.assertAttributesEqual(tag1, {
            'foo': True,
            'bar': True,
        })
        self.assertAttributesEqual(tag2, {
            'baz': True,
        })

    def test_attributes_mixed(self):
        # Even dirtier
        # Note that there is %(...)(...)
        tree = parse_string(jl(
            '%( foo_bar-baz \t = \'lol\' \t)( spam = eggs i_feel-great- \t lmao=" rofl\t\'")',
        )).tree
        tag, = tree.children
        self.assertAttributesEqual(tag, {
            'foo_bar-baz': 'lol',
            'spam': 'eggs',
            'i_feel-great-': True,
            'lmao': " rofl\t'",
        })

    def test_attributes_multiline(self):
        tree = parse_string(jl(
            '%( ',
            '   spam = eggs ',
            'herp="derp"',
            ')',
        )).tree
        tag, = tree.children
        self.assertAttributesEqual(tag, {
            'spam': 'eggs',
            'herp': 'derp',
        })

    def test_python_attributes(self):
        # Even dirtier
        tree = parse_string(jl(
            '%{"sup":"nah"}{"at"+"tribute": ("value"*2).upper()}',
        )).tree
        tag, = tree.children
        self.assertAttributesEqual(tag, {
            'attribute': 'VALUEVALUE',
            'sup': 'nah',
        })

    def test_python_attributes_multiline(self):
        # Even dirtier
        tree = parse_string(jl(
            '%{',
            '\t    "sup":  "nah"',
            ' } %{',
            '   "at"+"tri"',
            '      "bute": (',
            '"value"*2).upper()',
            '   }',
        )).tree
        tag1, = tree.children
        tag2, = tag1.children
        self.assertAttributesEqual(tag1, {
            'sup': 'nah',
        })
        self.assertAttributesEqual(tag2, {
            'attribute': 'VALUEVALUE',
        })
    
    def test_for_stupid_readahead(self):
        tree = parse_string(jl(
            '%{}',
            '%()',
            '%{ \t }',
            '%( \t )',
            '%{}',
            '%()',
            '%{ \t }',
            '%( \t )',
            '%a',
        )).tree
        self.assertEqual(len(tree.children), 9)

    def test_entity_decode(self):
        tree = parse_string(jl(
            '%&Aacute;.&Aacute;#&Aacute;(&Aacute;="&quot;&apos;&Aacute;")',
        )).tree
        tag1, = tree
        self.assertEqual(tag1.name, '\u00c1')
        self.assertEqual(tag1.id_, '\u00c1')
        self.assertSetEqual(tag1.classes, {'\u00c1'})
        self.assertDictEqual(
            tag1.attributes_set[0],
            {'\u00c1': '"\'\u00c1'},
        )

