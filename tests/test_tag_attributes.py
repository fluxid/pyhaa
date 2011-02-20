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

from unittest import TestCase

from pyhaa import (
    parse_string,
)

from .helpers import jl

class TestTagAttributes(TestCase):
    def test_empty_attributes(self):
        tree = parse_string(jl(
            '%',
            '%(){}()',
            '%( \t     ){  \t  }',
        ))
        tag1, tag2, tag3 = tree.children
        self.assertDictEqual(tag1.simple_attributes, {})
        self.assertDictEqual(tag2.simple_attributes, {})
        self.assertDictEqual(tag3.simple_attributes, {})
        self.assertIs(tag1.python_attributes, None)
        self.assertIs(tag2.python_attributes, None)
        self.assertIs(tag3.python_attributes, None)

    def test_attributes_names(self):
        # Dirty style but still valid
        tree = parse_string(jl(
            '%(foo \t bar)',
            '%( \t baz\t \t)',
        ))
        tag1, tag2 = tree.children
        self.assertDictEqual(tag1.simple_attributes, {
            'foo': True,
            'bar': True,
        })
        self.assertDictEqual(tag2.simple_attributes, {
            'baz': True,
        })

    def test_attributes_mixed(self):
        # Even dirtier
        # Note that there is %(...)(...)
        tree = parse_string(jl(
            '%( foo_bar-baz \t = \'lol\' \t)( spam = eggs i_feel-great- \t lmao=" rofl\t\'")',
        ))
        tag, = tree.children
        self.assertDictEqual(tag.simple_attributes, {
            'foo_bar-baz': 'lol',
            'spam': 'eggs',
            'i_feel-great-': True,
            'lmao': " rofl\t'",
        })

    def test_python_attributes(self):
        # Even dirtier
        tree = parse_string(jl(
            '%{sup:nah}{"at"+"tribute": ("value"*2).upper()}',
        ))
        tag, = tree.children
        self.assertDictEqual(eval(tag.python_attributes), {
            'attribute': 'VALUEVALUE',
        })

