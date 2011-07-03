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

from collections import Counter

class TemplateCache:
    def __init__(self, size, check_every=10):
        self.size = size
        self.check_every = check_every

        self.gets = 0
        self.values = {}
        self.uses = Counter()
        # TODO
        self.lock = None

    def store(self, key, value):
        self.values[key] = value
        self.uses[key] = 0

    def get(self, key):
        value = self.values.get(key)
        if value is None:
            return None
        # Substract, so most_common will actually return least commonly used
        self.uses[key] -= 1

        self.gets = (self.gets + 1) % self.check_every
        if not self.gets:
            for key, _ in self.uses.most_common(len(self.values) - self.size):
                self.remove(key)
        
        return value
        
    def remove(self, key):
        del self.values[key]
        del self.uses[key]

    def clear(self):
        self.gets = 0
        self.values.clear()
        self.uses.clear()

