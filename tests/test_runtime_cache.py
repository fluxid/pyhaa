# -*- coding: utf-8 -*-

'''
Testing cache
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

from pyhaa.runtime.cache import LFUCache

class TestCache(TestCase):
    def test_template_cache(self):
        cache = LFUCache(2, 2)
        # template cache doesn't really care about what is stored in it
        cache.store('a', 'a!')
        cache.store('b', 'b!')
        cache.store('c', 'c!')
        cache.store('d', 'd!')
        self.assertEqual(cache.get('d'), 'd!')
        self.assertEqual(cache.get('a'), 'a!')
        self.assertEqual(cache.get('d'), 'd!')
        self.assertEqual(cache.get('a'), 'a!')
        self.assertEqual(cache.get('c'), 'c!')
        cache.store('e', 'e!')
        # In above call cache should be cleaned up
        # Correct guess are b (used once) and b (never used)
        self.assertEqual(cache.get('c'), None)
        self.assertEqual(cache.get('b'), None)
        self.assertEqual(cache.get('d'), 'd!')
        self.assertEqual(cache.get('a'), 'a!')
        self.assertEqual(cache.get('a'), 'a!')
        self.assertEqual(cache.get('e'), 'e!')
        self.assertEqual(cache.get('e'), 'e!')
        cache.store('f', 'f!')
        cache.store('g', 'g!')
        # f - zero uses. Sorry, it didn't make it
        self.assertEqual(cache.get('f'), None)
        # g was added after cleanup
        self.assertEqual(cache.get('g'), 'g!')
        # e had more (two) uses than f but got removed too
        self.assertEqual(cache.get('e'), None)
        # a and d still on top...
        self.assertEqual(cache.get('d'), 'd!')
        self.assertEqual(cache.get('a'), 'a!')

        # Duh, we shouldn't touch internals...
        self.assertEqual(cache.offset, 3)
        self.assertEqual(cache.cachedict['a'].priority, 5)
        self.assertEqual(cache.cachedict['d'].priority, 4)
        cache.reduce_offset()
        self.assertEqual(cache.offset, 0)
        self.assertEqual(cache.cachedict['a'].priority, 2)
        self.assertEqual(cache.cachedict['d'].priority, 1)

