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

from . import (
    byterepr,
    CodeGen,
)
from ..runtime import (
    html,
    merge_element_attributes,
    prepare_for_tag,
)

class HTMLCodeGen(CodeGen):
    superclass_name = 'HTMLTemplate'
    imports = (
        'from pyhaa.runtime.html import HTMLTemplate',
    )
    void_tags = set((
        'area',
        'base',
        'br',
        'col',
        'command',
        'embed',
        'hr',
        'img',
        'input',
        'keygen',
        'link',
        'meta',
        'param',
        'source',
        'track',
        'wbr',
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_name_stack = list()

    def tag_is_self_closing(self, node):
        if node.name in self.void_tags:
            if node.children:
                # TODO: Raise more verbose exception
                # Void tags can't have any children in HTML
                raise Exception
            return True
        return False

    def tag_is_static(self, node):
        return not node.attributes_set or len(node.attributes_set) == 1 and not isinstance(node.attributes_set[0], str)

    def open_tag(self, name, id_, classes, attributes, self_close):
        name, attributes = prepare_for_tag(name, merge_element_attributes(id_, classes, attributes))
        self.write_io(
            "yield {}".format(repr(b''.join(html.open_tag(
                name,
                attributes,
                self_close,
            )))),
        )
        if not self_close:
            self.tag_name_stack.append(name)

    def close_tag(self):
        self.write_io(
            "yield {}".format(repr(b''.join(html.close_tag(self.tag_name_stack.pop())))),
        )

    def handle_open_tag(self, node):
        self_close = self.tag_is_self_closing(node)
        if self.tag_is_static(node):
            self.open_tag(
                node.name,
                node.id_,
                node.classes,
                node.attributes_set,
                self_close,
            )
        else:
            self.write_io(
                'yield self.open_tag({}, {}, {}, {}, {})'.format(
                    byterepr(node.name),
                    byterepr(node.id_),
                    byterepr(node.classes or None),
                    '[{}]'.format(', '.join((
                        (attributes if isinstance(attributes, str) else repr({
                            byterepr(key): byterepr(value)
                            for key, value in attributes.items()
                        })).strip()
                        for attributes in node.attributes_set
                    ))),
                    byterepr(self_close),
                ),
            )

    def handle_close_tag(self, node):
        if self.tag_is_self_closing(node):
            return
        if self.tag_is_static(node):
            self.close_tag()
        else:
            self.write_io(
                'yield self.close_tag()',
            )

    def handle_open_text(self, node):
        self.write_io(
            'yield {}'.format(byterepr(node.text)),
        )

