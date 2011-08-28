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

from .helpers import jl, PyhaaTestCase

class TestBasicTags(PyhaaTestCase):
    def test_one_tag(self):
        structure = self.senv.parse_string(jl(
            '%',
        ))
        # All tags are closed
        self.assertIs(structure.current, structure.tree)
        # Root has one child
        self.assertEqual(len(structure.tree), 1)
        child, = structure.tree
        # No siblings!
        self.assertIs(child.next_sibling, None)
        self.assertIs(child.prev_sibling, None)
        # Check for correct parrent and root
        self.assertIs(child.parent, structure.tree)
        self.assertIs(child.root, structure.tree)
        # No children ever added
        self.assertEqual(len(child.children), 0)

    def test_two_tags(self):
        structure = self.senv.parse_string(jl(
            '%',
            '%',
        ))
        # All tags are closed
        self.assertIs(structure.current, structure.tree)
        # Two children, cool!
        self.assertEqual(len(structure.tree), 2)
        child1, child2 = structure.tree
        # They're each other siblings!
        self.assertIs(child1.next_sibling, child2)
        self.assertIs(child2.prev_sibling, child1)
        # Check for correct parrent and root
        self.assertIs(child2.parent, structure.tree)
        self.assertIs(child2.root, structure.tree)
        # Second one is sibling, not child
        self.assertEqual(len(child1.children), 0)

    def test_one_child(self):
        structure = self.senv.parse_string(jl(
            '%',
            '\t%',
        ))
        # All tags are closed
        self.assertIs(structure.current, structure.tree)
        # Root is parent of one child
        self.assertEqual(len(structure.tree), 1)
        child1, = structure.tree
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
        self.assertIs(subchild1.root, structure.tree)

    def test_one_child_and_sibling(self):
        structure = self.senv.parse_string(jl(
            '%',
            '\t%',
            '%',
        ))
        # Again, all tags are closed
        self.assertIs(structure.current, structure.tree)
        # Root is parent of two children
        self.assertEqual(len(structure.tree), 2)
        child1, child2 = structure.tree
        # Again, they're each other siblings!
        self.assertIs(child1.next_sibling, child2)
        self.assertIs(child2.prev_sibling, child1)
        # First one has a child!
        self.assertEqual(len(child1.children), 1)
        subchild1 = child1.children[0]
        # But the second one does not...
        self.assertEqual(len(child2.children), 0)
        # Aaand, check if sibling parent is really root
        self.assertIs(child2.parent, structure.tree)

    def test_one_child_and_sibling_inline(self):
        # Same as in test_one_child_and_sibling, but we use inline notation
        structure = self.senv.parse_string(jl(
            '% %',
            '%',
        ))
        # Again, all tags are closed
        self.assertIs(structure.current, structure.tree)
        # Root is parent of two children
        self.assertEqual(len(structure.tree), 2)
        child1, child2 = structure.tree
        # Again, they're each other siblings!
        self.assertIs(child1.next_sibling, child2)
        self.assertIs(child2.prev_sibling, child1)
        # First one has a child!
        self.assertEqual(len(child1.children), 1)
        subchild1 = child1.children[0]
        # But the second one does not...
        self.assertEqual(len(child2.children), 0)
        # Aaand, check if sibling parent is really root
        self.assertIs(child2.parent, structure.tree)

    def test_three_levels(self):
        # Let's use two spaces intead of tabs this time...
        structure = self.senv.parse_string(jl(
            '%',
            '  %',
            '    %',
        ))
        # Of course, all tags are closed
        self.assertIs(structure.current, structure.tree)
        # Let's get straight to children
        tag1, = structure.tree
        tag2, = tag1
        tag3, = tag2
        # Cool! What about parents?
        self.assertIs(tag1.parent, structure.tree)
        self.assertIs(tag2.parent, tag1)
        self.assertIs(tag3.parent, tag2)
        # ...or root?
        self.assertIs(tag1.root, structure.tree)
        self.assertIs(tag2.root, structure.tree)
        self.assertIs(tag3.root, structure.tree)

    def test_children_of_inline(self):
        structure = self.senv.parse_string(jl(
            '%a %b', # tag1 tag2
            '  %c', # tag3
            '  %d', # tag4
            '%e', # tag5
        ))
        # Let's be sure
        self.assertIs(structure.current, structure.tree)
        #import pdb; pdb.set_trace()
        # Root is parent of two children
        self.assertEqual(len(structure.tree), 2)
        # Let's get straight to children
        tag1, tag5 = structure.tree
        tag2, = tag1
        tag3, tag4 = tag2
        # Cool! What about parents?
        self.assertIs(tag1.parent, structure.tree)
        self.assertIs(tag2.parent, tag1)
        self.assertIs(tag3.parent, tag2)
        self.assertIs(tag4.parent, tag2)
        self.assertIs(tag5.parent, structure.tree)
        # ...or root?
        self.assertIs(tag1.root, structure.tree)
        self.assertIs(tag2.root, structure.tree)
        self.assertIs(tag3.root, structure.tree)
        self.assertIs(tag4.root, structure.tree)
        self.assertIs(tag5.root, structure.tree)
        # Nice family we got here!
        self.assertIs(tag3.next_sibling, tag4)
        self.assertIs(tag4.prev_sibling, tag3)

    def test_deep(self):
        '''
        Test deep structures, as I'm not 100% sure
        if dedent and node closing works correctly.
        '''
        structure = self.senv.parse_string(jl(
            '% % %', # 1 3 4
            '  % %', # 5 7
            '    % % %', # 8 9 10
            '      % %', # 11 13
            '      %', # 12
            '  % %', # 6 14
            '    % %', # 15 16
            '      %', # 17
            '      % %', # 18 19
            '%', # 2
        ))
        # Let's be sure
        self.assertIs(structure.current, structure.tree)
        # Unfold tree
        tag1, tag2 = structure.tree
        tag3, = tag1
        tag4, = tag3
        tag5, tag6 = tag4
        tag7, = tag5
        tag8, = tag7
        tag9, = tag8
        tag10, = tag9
        tag11, tag12 = tag10
        tag13, = tag11
        tag14, = tag6
        tag15, = tag14
        tag16, = tag15
        tag17, tag18 = tag16
        tag19, = tag18

