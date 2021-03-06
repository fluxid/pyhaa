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

import logging

from  .. import structure
from ..utils.cgrt_common import (
    close_tag,
    open_tag,
    prepare_for_tag,
)
from ..utils.encode import single_encode

from . import CodeGen

log = logging.getLogger(__name__)

class HTMLCodeGen(CodeGen):
    imports = CodeGen.imports + (
        'from pyhaa.utils.encode import single_encode as _ph_single_encode',
        'from pyhaa.runtime.html import _ph_open_tag, _ph_close_tag',
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
        self.simple_bytes = list()
        self.simple_bytes_indent_level = self.indent_level
        self.last_was_text = False

    def call_node_handling_function(self, prefix, node):
        super().call_node_handling_function(prefix, node)
        self.last_was_text = isinstance(node, structure.Text)

    def write_simple_bytes(self, *args):
        if self.simple_bytes_indent_level != self.indent_level:
            self.flush_simple_bytes()
            self.simple_bytes_indent_level = self.indent_level
        self.simple_bytes.extend(args)

    def flush_simple_bytes(self):
        if self.simple_bytes:
            self.write_io(
                'yield {}'.format(repr(b''.join(self.simple_bytes))),
                flush_simple_bytes = False,
                indent_level = self.simple_bytes_indent_level,
            )
            del self.simple_bytes[::]

    def write_io(self, *args, flush_simple_bytes = True, **kwargs):
        if flush_simple_bytes:
            log.debug('Flushing simple bytes')
            self.flush_simple_bytes()
        return super().write_io(*args, **kwargs)

    def write(self, *args, **kwargs):
        super().write(*args, **kwargs)
        self.flush_simple_bytes()

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

    def open_template_function(self, *args, **kwargs):
        super(HTMLCodeGen, self).open_template_function(*args, **kwargs)
        self.write_io(
            # Holy shit, i don't like this...
            '_ph_tag_name_stack = []',
        )

    def open_tag(self, name, id_, classes, attributes, self_close):
        name, attributes = prepare_for_tag(name, id_, classes, attributes, True, True, self.encoding)
        self.write_simple_bytes(
            b''.join(open_tag(
                name,
                attributes,
                self_close,
            )),
        )
        if not self_close:
            self.tag_name_stack.append(name)

    def close_tag(self):
        tag_name = self.tag_name_stack.pop()
        log.debug('closing tag %s', tag_name)
        self.write_simple_bytes(
            b''.join(close_tag(tag_name)),
        )

    def handle_open_tag(self, node):
        self_close = self.tag_is_self_closing(node)
        self.autoclose_open_node(node)
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
                'yield _ph_open_tag(_ph_tag_name_stack, {}, {}, {}, {}, {}, {})'.format(
                    self.byterepr(node.name),
                    self.byterepr(node.id_),
                    self.byterepr(node.classes or None),
                    '[{}]'.format(', '.join((
                        (attributes if isinstance(attributes, str) else repr({
                            single_encode(key, True, True, self.encoding):
                            single_encode(value, True, True, self.encoding)
                            for key, value in attributes.items()
                        })).strip()
                        for attributes in node.attributes_set
                    ))),
                    self.byterepr(self_close),
                    repr(self.encoding),
                ),
            )

    def handle_close_tag(self, node):
        self.autoclose_close_node()
        if self.tag_is_self_closing(node):
            return
        if self.tag_is_static(node):
            self.close_tag()
        else:
            self.write_io(
                'yield _ph_close_tag(_ph_tag_name_stack)',
            )

    def handle_open_text(self, node):
        if self.last_was_text:
            self.write_simple_bytes(
                b' ',
            )
        self.write_simple_bytes(
            single_encode(node.content, True, node.escape, self.encoding),
        )

    def handle_open_expression(self, node):
        self.write_io(
            'yield _ph_single_encode(({}), True, {}, self.encoding, True, True)'.format(
                node.content,
                repr(node.escape),
            ),
        )

    def byterepr(self, value):
        return repr(single_encode(value, True, True, self.encoding))

    # Autoclosing
    def autoclose_close_func(self):
        # Save state
        tmp_tags = list(self.tag_name_stack)
        super().autoclose_close_func()
        self.tag_name_stack = tmp_tags

    def autoclose_close_loop(self):
        # Save state
        tmp_tags = list(self.tag_name_stack)
        super().autoclose_close_loop()
        self.tag_name_stack = tmp_tags

