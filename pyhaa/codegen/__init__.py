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

import itertools
import logging
import re

from .. import (
    structure,
    utils,
)

DEFAULT_INDENT_STRING = '    '
DEFAULT_NEWLINE = '\n'
DEFAULT_ENCODING = 'utf-8'

log = logging.getLogger(__name__)


def name_node_handling_function(prefix, node):
    return 'handle_' + prefix + utils.decamel(node.__class__.__name__)

def or_if_none(value, replacement):
    if value is None:
        return replacement
    return value

class CodeGen:
    imports = (
        'from pyhaa.runtime import encapsulate_exceptions as _ph_encapsulate_exceptions, TemplateInfo as _ph_TemplateInfo',
    )

    def __init__(self, structure, io, **kwargs):
        indent_string = or_if_none(kwargs.get('indent_string'), DEFAULT_INDENT_STRING)
        newline = or_if_none(kwargs.get('newline'), DEFAULT_NEWLINE)
        encoding = or_if_none(kwargs.get('encoding'), DEFAULT_ENCODING)

        template_path = kwargs.get('template_path')
        template_name = kwargs.get('template_name') or template_path or '!template_{}'.format(id(structure))


        self.structure = structure
        self.io = io
        self.indent_string = indent_string.encode(encoding)
        self.newline = newline.encode(encoding)
        self.encoding = encoding
        self.template_path = template_path
        self.template_name = template_name

        # What to autoclose in case of return, break or continue statements
        # For returns
        self.func_stack = []
        # For continues and breaks
        self.loop_stack = []
        # Whether we're in the process of autoclosing nodes
        self.autoclosing_now = False

        self.written_partials = set()
        self.indent_level = 0
        self.ignore_code_level = 0

    def indent(self, times=1):
        if times > 0:
            self.indent_level += times

    def dedent(self, times=1):
        if self.indent_level and times > 0:
            self.indent_level -= min(times, self.indent_level)

    def write_io(self, *args, indent_level=None):
        if indent_level is None:
            indent_level = self.indent_level

        if self.ignore_code_level:
            if indent_level >= self.ignore_code_level:
                return
            if self.indent_level < self.ignore_code_level:
                self.ignore_code_level = 0

        if len(args) == 1 and hasattr(args[0], '__next__'):
            args, = args
        for arg in args:
            if indent_level:
                self.io.write(indent_level * self.indent_string)
            self.io.write(arg.encode(self.encoding))
            self.io.write(self.newline)

    def write_file_header(self):
        self.write_io(
            '# -*- coding: {} -*-'.format(self.encoding),
        )

    def write_inheritance(self):
        self.write_io(
            'inheritance = lambda: ({}),'.format(' '.join((
                '({}),'.format(inherits)
                for inherits in self.structure.inheritance
            ))),
        )

    def write_base_imports(self):
        self.write_io(
            iter(self.imports)
        )

    def open_template_function(self, name, attributes=None):
        attributes = attributes.lstrip() if attributes else ''
        if attributes and not attributes.startswith(','):
            attributes = ', ' + attributes

        self.write_io(
            # Register template in template_info...
            '@_ph_template_info.register_partial',
            'def {}(self, parent{}):'.format(
                name,
                attributes,
            ),
        )
        self.indent()
        self.write_io(
            'with _ph_encapsulate_exceptions():',
        )
        self.autoclose_open_func()
        self.indent()

        self.written_partials.add(name)

    def close_template_function(self, name):
        self.dedent(2)
        # This gets worse by time...
        # Remove so it doesn't get into globals so we can't
        # call it directly
        self.write_io('del {}'.format(name))

    def write_root_node_function(self, node, empty_iter=False):
        if len(node) == 0 and not empty_iter:
            # Don't write anything
            return

        self.node_open(node)
        if len(node) == 0 and empty_iter:
            self.write_io(
                'if False: yield',
            )
        else:
            self.write_root_node_contents(node, empty_iter)
        self.node_close(node)

    def write_root_node_contents(self, node, empty_iter=False):
        # In this case as "root node" we mean node which is the topmost parent

        iter_stack = list()
        node_stack = list()
        current_iter = iter(node)

        while True:
            node = next(current_iter, None)
            if node is None:
                if node_stack:
                    self.node_close(node_stack.pop())
                if not iter_stack:
                    while node_stack:
                        self.node_close(node_stack.pop())
                    break
                current_iter = iter_stack.pop()
                continue

            self.node_open(node)
            if isinstance(node, structure.PyhaaParent):
                node_stack.append(node)
                iter_stack.append(current_iter)
                current_iter = iter(node)
            else:
                self.node_close(node)

    def write_partials(self):
        # Partials
        for partial in self.structure.partials.values():
            self.write_root_node_function(partial, True)

        # Body
        self.write_root_node_function(self.structure.tree)

    def write_attributes(self):
        self.write_io(
            'encoding = {},'.format(repr(self.encoding)),
            'template_path = {},'.format(repr(self.template_path)),
            'template_name = {},'.format(repr(self.template_name)),
        )

    def write_template_info(self):
        self.write_io(
            '_ph_template_info = _ph_TemplateInfo(',
        )
        self.indent()

        self.write_attributes()
        self.write_inheritance()
        #self.write_partials_dict()

        self.dedent()
        self.write_io(
            ')',
        )

    def write(self):
        self.write_file_header()
        self.write_base_imports()
        self.write_template_info()
        self.write_partials()

    def node_open(self, node):
        self.call_node_handling_function('open', node)
        if isinstance(node, structure.CompoundStatement):
            self.indent()

    def node_close(self, node):
        self.call_node_handling_function('close', node)
        if isinstance(node, structure.CompoundStatement):
            self.dedent()

    def call_node_handling_function(self, prefix, node):
        if node is None: # pragma: no cover
            return
        function_name = name_node_handling_function(prefix, node)
        function = getattr(self, function_name, None)
        if function:
            log.debug("Found function %s for node %r.", function_name, node)
            function(node)
        else:
            log.warning("Couldn't find function %s for node %r.", function_name, node)

    def handle_open_pyhaa_tree(self, node):
        self.open_template_function('__body__', '*arguments, **keywords')

    def handle_close_pyhaa_tree(self, node):
        self.close_template_function('__body__')

    def handle_open_pyhaa_partial(self, node):
        self.open_template_function(node.name, node.arguments)

    def handle_close_pyhaa_partial(self, node):
        self.close_template_function(node.name)

    def handle_open_simple_statement(self, node):
        if node.name == 'return':
            self.autoclose_close_func()
        elif node.name in ('break', 'continue'):
            self.autoclose_close_loop()
        self.write_io(
            node.content,
        )
        if node.name in ('return', 'break', 'continue'):
            self.ignore_code_level = self.indent_level

    def handle_open_compound_statement(self, node):
        self.write_io(
            node.content,
        )
        if node.name in ('for', 'while'):
            self.autoclose_open_loop()

    def handle_close_compound_statement(self, node):
        if node.name in ('for', 'while'):
            self.autoclose_pop_loop()

    # Autoclosing
    def autoclose_open_func(self):
        self.func_stack.append([])

    def autoclose_open_loop(self):
        self.loop_stack.append([])

    def autoclose_nodes(self, node_stack):
        self.autoclosing_now = True
        for node in reversed(node_stack):
            self.node_close(node)
        self.autoclosing_now = False

    def autoclose_close_func(self):
        # Subclasses should clone internal state here if any of the closing functions modify it
        if self.func_stack:
            self.autoclose_nodes(self.func_stack[-1])

    def autoclose_close_loop(self):
        # Subclasses should clone internal state here if any of the closing functions modify it
        if self.loop_stack:
            self.autoclose_nodes(self.loop_stack[-1])

    def autoclose_pop_func(self):
        if self.func_stack:
            self.func_stack.pop()

    def autoclose_pop_loop(self):
        if self.loop_stack:
            self.loop_stack.pop()

    def autoclose_open_node(self, node):
        if self.func_stack:
            self.func_stack[-1].append(node)
        if self.loop_stack:
            self.loop_stack[-1].append(node)

    def autoclose_close_node(self):
        if self.autoclosing_now:
            return
        if self.func_stack:
            node_stack = self.func_stack[-1]
            if node_stack:
                node_stack.pop()
        if self.loop_stack:
            node_stack = self.loop_stack[-1]
            if node_stack:
                node_stack.pop()

