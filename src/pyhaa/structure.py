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

class PyhaaParent:
    def __init__(self, **kwargs):
        self.children = list()
        self.root = self
        super().__init__(**kwargs)

    def append(self, other):
        other.root = self.root
        other.parent = self
        if self.children:
            last = self.children[-1]
            last.next_sibling = other
            other.prev_sibling = last
        self.children.append(other)
        return self
    
    def __iter__(self):
        return iter(self.children)


class PyhaaTree(PyhaaParent):
    def __init__(self):
        self.current = self
        super().__init__()

    def append(self, other):
        if self.current is self:
            super().append(other)
        else:
            self.current.append(other)
        self.current = other

    def close(self, times = 1):
        for i in range(times):
            if self.current is not self:
                self.current = self.current.parent


class PyhaaElement:
    def __init__(self, ws_out_left = True, ws_out_right = True):
        self.parent = None
        self.root = None
        self.prev_sibling = None
        self.next_sibling = None
        self.ws_out_left = ws_out_left
        self.ws_out_right = ws_out_right

    def append(self, other):
        raise Exception("Can\'t append children to normal element")


class PyhaaElementOpenable(PyhaaParent, PyhaaElement):
    def __init__(self, ws_in_left = True, ws_in_right = True, **kwargs):
        self.ws_in_left = ws_in_left
        self.ws_in_right = ws_in_right
        super().__init__(**kwargs)


class Tag(PyhaaElementOpenable):
    def __init__(self, name = None, id_ = None, classes = None, simple_attributes = None, python_attributes = None, **kwargs):
        self._classes = None
        self._simple_attributes = None
        self._python_attributes = None

        self.name = name
        self.id_ = id_
        self.classes = classes
        self.simple_attributes = simple_attributes
        self.python_attributes = python_attributes
        super().__init__(**kwargs)

    def _get_classes(self):
        return self._classes

    def _set_classes(self, value):
        self._classes = set(value) if value else set()

    classes = property(_get_classes, _set_classes)

    def _get_simple_attributes(self):
        return self._simple_attributes

    def _set_simple_attributes(self, value):
        self._simple_attributes = dict(value) if value else dict()

    simple_attributes = property(_get_simple_attributes, _set_simple_attributes)

    def _get_python_attributes(self):
        return self._python_attributes

    def _set_python_attributes(self, value):
        if not value or value == '{}':
            value = None
        self._python_attributes = value

    python_attributes = property(_get_python_attributes, _set_python_attributes)


class Text(PyhaaElement):
    def __init__(self, text = None, escape = True, **kwargs):
        self.text = text
        self.escape = escape
        super().__init__(**kwargs)

class ModuleLevel:
    pass

class ClassLevel:
    pass
