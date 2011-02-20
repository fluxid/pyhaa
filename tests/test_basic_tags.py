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

class TestBasicTags(TestCase):
    def test_one_tag(self):
        tree = parse_string(jl(
            '%',
        ))
        # All tags are closed
        self.assertIs(tree.current, tree)
        # Root has one child
        self.assertEqual(len(tree.children), 1)
        child = tree.children[0]
        # No siblings!
        self.assertIs(child.next_sibling, None)
        self.assertIs(child.prev_sibling, None)
        # Check for correct parrent and root
        self.assertIs(child.parent, tree)
        self.assertIs(child.root, tree)
        # No children ever added
        self.assertEqual(len(child.children), 0)

    def test_two_tags(self):
        tree = parse_string(jl(
            '%',
            '%',
        ))
        # All tags are closed
        self.assertIs(tree.current, tree)
        # Two children, cool!
        self.assertEqual(len(tree.children), 2)
        child1 = tree.children[0]
        child2 = tree.children[1]
        # They're each other siblings!
        self.assertIs(child1.next_sibling, child2)
        self.assertIs(child2.prev_sibling, child1)
        # Check for correct parrent and root
        self.assertIs(child2.parent, tree)
        self.assertIs(child2.root, tree)
        # Second one is sibling, not child
        self.assertEqual(len(child1.children), 0)

    def test_one_child(self):
        tree = parse_string(jl(
            '%',
            '\t%',
        ))
        # All tags are closed
        self.assertIs(tree.current, tree)
        # Root is parent of one child
        self.assertEqual(len(tree.children), 1)
        child1 = tree.children[0]
        # Check if it really has no siblings..
        self.assertIs(child1.next_sibling, None)
        self.assertIs(child1.prev_sibling, None)
        # It has a child! Call it a subchild...
        self.assertEqual(len(child1.children), 1)
        subchild1 = child1.children[0]
        # It doesn't have any siblings either
        self.assertIs(subchild1.next_sibling, None)
        self.assertIs(subchild1.prev_sibling, None)
        # Check for correct parrent and root
        self.assertIs(subchild1.parent, child1)
        self.assertIs(subchild1.root, tree)

    def test_one_child_and_sibling(self):
        tree = parse_string(jl(
            '%',
            '\t%',
            '%',
        ))
        # Again, all tags are closed
        self.assertIs(tree.current, tree)
        # Root is parent of two children
        self.assertEqual(len(tree.children), 2)
        child1 = tree.children[0]
        child2 = tree.children[1]
        # Again, they're each other siblings!
        self.assertIs(child1.next_sibling, child2)
        self.assertIs(child2.prev_sibling, child1)
        # First one has a child!
        self.assertEqual(len(child1.children), 1)
        subchild1 = child1.children[0]
        # But the second one does not...
        self.assertEqual(len(child2.children), 0)
        # Aaand, check if sibling parent is really root
        self.assertIs(child2.parent, tree)

    def test_one_child_and_sibling_inline(self):
        # Same as in test_one_child_and_sibling, but we use inline notation
        tree = parse_string(jl(
            '% %',
            '%',
        ))
        # Again, all tags are closed
        self.assertIs(tree.current, tree)
        # Root is parent of two children
        self.assertEqual(len(tree.children), 2)
        child1 = tree.children[0]
        child2 = tree.children[1]
        # Again, they're each other siblings!
        self.assertIs(child1.next_sibling, child2)
        self.assertIs(child2.prev_sibling, child1)
        # First one has a child!
        self.assertEqual(len(child1.children), 1)
        subchild1 = child1.children[0]
        # But the second one does not...
        self.assertEqual(len(child2.children), 0)
        # Aaand, check if sibling parent is really root
        self.assertIs(child2.parent, tree)

    def test_three_levels(self):
        # Let's use two spaces intead of tabs this time...
        tree = parse_string(jl(
            '%',
            '  %',
            '    %',
        ))
        # Of course, all tags are closed
        self.assertIs(tree.current, tree)
        # Let's get straight to children
        tag1 = tree.children[0]
        tag2 = tag1.children[0]
        tag3 = tag2.children[0]
        # Cool! What about parents?
        self.assertIs(tag1.parent, tree)
        self.assertIs(tag2.parent, tag1)
        self.assertIs(tag3.parent, tag2)
        # ...or root?
        self.assertIs(tag1.root, tree)
        self.assertIs(tag2.root, tree)
        self.assertIs(tag3.root, tree)

    def test_children_of_inline(self):
        tree = parse_string(jl(
            '% %', # tag1 tag2
            '  %', # tag3
            '  %', # tag4
            '%', # tag5
        ))
        # Let's be sure
        self.assertIs(tree.current, tree)
        # Root is parent of two children
        self.assertEqual(len(tree.children), 2)
        # Let's get straight to children
        tag1 = tree.children[0]
        tag2 = tag1.children[0]
        tag3 = tag2.children[0]
        tag4 = tag2.children[1]
        tag5 = tree.children[1]
        # Cool! What about parents?
        self.assertIs(tag1.parent, tree)
        self.assertIs(tag2.parent, tag1)
        self.assertIs(tag3.parent, tag2)
        self.assertIs(tag4.parent, tag2)
        self.assertIs(tag5.parent, tree)
        # ...or root?
        self.assertIs(tag1.root, tree)
        self.assertIs(tag2.root, tree)
        self.assertIs(tag3.root, tree)
        self.assertIs(tag4.root, tree)
        self.assertIs(tag5.root, tree)
        # Nice family we got here!
        self.assertIs(tag3.next_sibling, tag4)
        self.assertIs(tag4.prev_sibling, tag3)

