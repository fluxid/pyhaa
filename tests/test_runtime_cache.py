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

from pyhaa.runtime.cache import TemplateCache

class TestCache(TestCase):
    def test_template_cache(self):
        cache = TemplateCache(2, 5)
        # template cache doesn't really care about what is stored in it
        cache.store('a', 'a!')
        cache.store('b', 'b!')
        cache.store('c', 'c!')
        cache.store('d', 'd!')
        self.assertEqual(cache.get('d'), 'd!')
        self.assertEqual(cache.get('a'), 'a!')
        self.assertEqual(cache.get('d'), 'd!')
        self.assertEqual(cache.get('a'), 'a!')
        self.assertEqual(cache.get('c'), 'c!') # We should still have c
        # in above call part of cache should be cleared
        # Correct guess are b (used once) and b (never used)
        # a ad d should have the same use count == 0 now
        self.assertEqual(cache.get('c'), None)
        self.assertEqual(cache.get('b'), None)
        self.assertEqual(cache.get('d'), 'd!')
        self.assertEqual(cache.get('a'), 'a!')
        cache.store('e', 'e!')
        self.assertEqual(cache.get('a'), 'a!')
        self.assertEqual(cache.get('e'), 'e!')
        self.assertEqual(cache.get('e'), 'e!')
        # a and e both have 2 uses, and d only 1 use
        self.assertEqual(cache.get('d'), None)




