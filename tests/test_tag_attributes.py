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
        # This should simply pass
        tree = parse_string(jl(
            '%()',
            '%( \t     )',
        ))

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
        tree = parse_string(jl(
            '%( foo_bar-baz \t = \'lol\' \t spam = eggs i_feel-great- \t lmao=" rofl\t\'")',
        ))
        tag, = tree.children
        self.assertDictEqual(tag.simple_arguments, {
            'foo_bar-baz': 'lol',
            'spam': 'eggs',
            'i_feel-great-': True,
            'lmao': " rofl\t'",
        })


