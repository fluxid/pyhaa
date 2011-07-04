# -*- coding: utf-8 -*-

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

import heapq
from threading import RLock

class _CachedElement:
    __slots__ = ('value', 'priority')

    def __init__(self, value, priority):
        self.value = value
        self.priority = 0

class LFUCache:
    '''
    Dumb LFU "aging" cache
    '''
    def __init__(self, max_size, grace=20):
        self.max_size = max_size
        self.grace = grace

        self.offset = 0
        self.cachedict = {}

        # TODO
        self.lock = RLock()

    def store(self, key, value):
        with self.lock:
            self.try_cleanup()
            self.cachedict[key] = _CachedElement(value, self.offset)

    def try_cleanup(self):
        with self.lock:
            over = len(self.cachedict) - self.max_size
            if over - self.grace < 0:
                return

            smallest = heapq.nsmallest(over, self.cachedict.items(), lambda x: x[1].priority)
            # This is the lowest priority so use it as offset
            for key, _ in smallest:
                del self.cachedict[key]

            self.offset = min(x.priority for x in self.cachedict.values())
            # Reduce offset if too high?

    def reduce_offset(self):
        with self.lock:
            offset = self.offset
            for value in self.cachedict.values():
                value.priority -= offset
            self.offset = 0

    def get(self, key):
        with self.lock:
            element = self.cachedict.get(key)
            if element is None:
                return None
            element.priority += 1
            return element.value
        
    def remove(self, key):
        with self.lock:
            del self.cachedict[key]

    def clear(self):
        with self.lock:
            self.offset = 0
            self.cachedict.clear()


class BytecodeCache:
    pass

