# -*- coding: utf-8 -*-

'''
Test basic utility function
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

from pyhaa.utils.cgrt_common import (
    prepare_for_tag as pft,
)

class TestRuntimeBasic(TestCase):
    
    def test_prepare_for_tag(self):
        self.assertSequenceEqual(
            pft('z', 'a', 'b', []),
            ('z', {'id':'a', 'class':'b'})
        )
        self.assertSequenceEqual(
            pft('a', None, None, [{'_tag_name':'b'}]),
            ('b', {})
        )
        self.assertSequenceEqual(
            pft('b', None, None, [{'id':'', 'class':[]}]),
            ('b', {})
        )
        self.assertSequenceEqual(
            pft('a', None, None, [{'class':'a b'}]),
            ('a', {'class':'a b'})
        )
        self.assertSequenceEqual(
            pft('a', None, ['z'], [{'class':['a', 'b']}]),
            ('a', {'class':'a b'})
        )
        self.assertSequenceEqual(
            pft('z', 'a', ['b', 'c'], [{'_append_class':'d'}, {'_tag_name':'x'}]),
            ('x', {'id':'a', 'class':'b c d'})
        )
        self.assertSequenceEqual(
            pft('z', 'a', None, [{'id':None}, {'huh':False}]),
            ('z', {})
        )

