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

class Count:
    '''
    Minimalistic implementation of "mutable string"
    For use in Counter
    '''
    __slots__ = 'value'

    def __init__(self):
        self.value = 0

    def add(self, other):
        self.value += other
        return self.value

    def __lt__(self, other):
        return self.value < other.value

class Counter(dict):
    '''
    Alternative partial microimplementation of collections.Counter
    '''
    def least_used(self, n):
        return heapq.nsmallest(n, self.items(), lambda x: x[1].value)
    
    def normalize(self):
        minimum = -min(self.values()).value
        for value in self.values():
            value.add(minimum)

    def init(self, key):
        self[key] = Count()

class TemplateCache:
    '''
    Dumb aging LFU cache
    '''
    def __init__(self, size, grace=10):
        self.size = size
        self.grace = grace

        self.gets = 0
        self.values = {}
        self.uses = Counter()
        # TODO
        self.lock = None

    def store(self, key, value):
        self.values[key] = value
        self.uses.init(key)

    def get(self, key):
        value = self.values.get(key)
        if value is None:
            return None

        self.uses[key].add(1)

        self.gets = (self.gets + 1) % self.grace
        if not self.gets:
            for key, _ in self.uses.least_used(len(self.values) - self.size):
                self.remove(key)
            self.uses.normalize()
        
        return value
        
    def remove(self, key):
        del self.values[key]
        del self.uses[key]

    def clear(self):
        self.gets = 0
        self.values.clear()
        self.uses.clear()

class BytecodeCache:
    pass

