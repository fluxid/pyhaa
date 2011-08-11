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

import re

RE_FIRST_KEYWORD = re.compile(r'(\w+)\b\s*')

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

    def __len__(self):
        return len(self.children)

    def __repr__(self):
        return '<{} {} children>'.format(
            self.__class__.__name__,
            len(self.children),
        )


class PyhaaTree(PyhaaParent):
    pass


class PyhaaPartial(PyhaaTree):
    def __init__(self, name, arguments, **kwargs):
        self.name = name
        self.arguments = arguments
        super(PyhaaPartial, self).__init__(**kwargs)


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
    pass


class PyhaaStatement:
    def __init__(self, name = None, **kwargs):
        self.name = name.strip().lower() if name else None
        super().__init__(**kwargs)


class PyhaaStructure:
    '''
    Template document structure
    '''
    def __init__(self):
        # Contains main body node tree
        self.tree = PyhaaTree()
        # Contains list of expressions - inheritance info
        self.inheritance = []
        # Contains dict of tuples (parameters, tree) where key is partial name
        self.partials = dict()
        # Contains current tree we operate on
        self.current = self.tree
        # Contains stack of opened nodes
        self.opened = []

    def append(self, other):
        self.current.append(other)
        self.opened.append(self.current)
        self.current = other

    def open_partial(self, name, arguments):
        partial = PyhaaPartial(name=name, arguments=arguments)
        self.partials[name] = partial
        self.opened.append(self.current)
        self.current = partial

    def close(self, times = 1):
        while times > 0 and self.opened:
            self.current = self.opened.pop()
            times -= 1
        return times


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


class SimpleStatement(PyhaaStatement, PyhaaSimpleContent):
    def __init__(self, **kwargs):
        content = kwargs.get('content')
        name = None
        if content:
            m = RE_FIRST_KEYWORD.match(content)
            if m:
                keyword = m.group(1)
                if keyword in (
                    'assert',
                    'pass',
                    'del',
                    'return',
                    'yield',
                    'raise',
                    'break',
                    'continue',
                    'import',
                    'global',
                    'nonlocal',
                ):
                    name = keyword
        kwargs['name'] = name
        super().__init__(**kwargs)


class CompoundStatement(PyhaaStatement, PyhaaParentNode, PyhaaSimpleContent):
    pass

