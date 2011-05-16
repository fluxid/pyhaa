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

# Base classes

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

    def __repr__(self):
        return '<{} {} children>'.format(
            self.__class__.__name__,
            len(self.children),
        )


class PyhaaTree(PyhaaParent):
    def __init__(self, **kwargs):
        self.current = self
        super().__init__(**kwargs)

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


class PyhaaNode:
    def __init__(self, **kwargs):
        self.parent = None
        self.root = None
        self.prev_sibling = None
        self.next_sibling = None
        super().__init__(**kwargs)

    def append(self, other):
        raise Exception("Can\'t append children to normal element")

    def __repr__(self):
        return '<{}>'.format(
            self.__class__.__name__,
        )


class PyhaaSimpleContent(PyhaaNode):
    def __init__(self, content = None, **kwargs):
        self.content = content
        super().__init__(**kwargs)

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            repr(self.content),
        )


class PyhaaEscapeableContent(PyhaaSimpleContent):
    def __init__(self, escape = True, **kwargs):
        self.escape = escape
        super().__init__(**kwargs)

    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            repr(self.content),
        )


class PyhaaParentNode(PyhaaParent, PyhaaNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ModuleLevel:
    '''
    Allows node to be on a module level (i.e. module-level code like import)
    '''
    pass


class ClassLevel:
    '''
    Allows node to be on a class module (i.e. helper function)
    '''
    pass


# Node types


class Tag(PyhaaParentNode):
    def __init__(self, name = None, id_ = None, classes = None, attributes_set = None, **kwargs):
        self._classes = None

        self.name = name
        self.id_ = id_
        self.classes = classes
        self.attributes_set = attributes_set or []
        super().__init__(**kwargs)

    def _get_classes(self):
        return self._classes

    def _set_classes(self, value):
        self._classes = set(value) if value else set()

    classes = property(_get_classes, _set_classes)

    def append_attributes(self, obj):
        if self.attributes_set and isinstance(obj, dict) and isinstance(self.attributes_set[-1], dict):
            self.attributes_set[-1].update(obj)
        else:
            self.attributes_set.append(obj)

    def __repr__(self):
        return '<{} {} {} children>'.format(
            self.__class__.__name__,
            repr(self.name),
            len(self.children),
        )


class Text(PyhaaEscapeableContent):
    pass


class Expression(PyhaaEscapeableContent):
    pass


class SimpleStatement(PyhaaSimpleContent):
    pass


class CompoundStatement(PyhaaParentNode, PyhaaSimpleContent):
    pass

