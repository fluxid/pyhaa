# -*- coding: utf-8 -*-

'''
Testing basic tag structures and pyhaa tree structure in general
'''

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
        self.assertDictEqual(tag1.simple_arguments, {})
        self.assertDictEqual(tag2.simple_arguments, {})
        self.assertDictEqual(tag3.simple_arguments, {})
        self.assertIs(tag1.python_arguments, None)
        self.assertIs(tag2.python_arguments, None)
        self.assertIs(tag3.python_arguments, None)

    def test_attributes_names(self):
        # Dirty style but still valid
        tree = parse_string(jl(
            '%(foo \t bar)',
            '%( \t baz\t \t)',
        ))
        tag1, tag2 = tree.children
        self.assertDictEqual(tag1.simple_arguments, {
            'foo': True,
            'bar': True,
        })
        self.assertDictEqual(tag2.simple_arguments, {
            'baz': True,
        })

    def test_attributes_mixed(self):
        # Even dirtier
        # Note that there is %(...)(...)
        tree = parse_string(jl(
            '%( foo_bar-baz \t = \'lol\' \t)( spam = eggs i_feel-great- \t lmao=" rofl\t\'")',
        ))
        tag, = tree.children
        self.assertDictEqual(tag.simple_arguments, {
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
        self.assertDictEqual(eval(tag.python_arguments), {
            'attribute': 'VALUEVALUE',
        })

