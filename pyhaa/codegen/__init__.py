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
DEFAULT_TEMPLATE_NAME = 'this_template'

log = logging.getLogger(__name__)


def name_node_handling_function(prefix, node):
    return 'handle_' + prefix + utils.decamel(node.__class__.__name__)

def or_if_none(value, replacement):
    if value is None:
        return replacement
    return value

class CodeGen:
    superclass_name = ''
    imports = (
        'from pyhaa.utils.encode import single_encode as _ph_single_encode',
        'from pyhaa.runtime import encapsulate_exceptions as _ph_encapsulate_exceptions',
    )

    def __init__(self, structure, io, **kwargs):
        indent_string = or_if_none(kwargs.get('indent_string'), DEFAULT_INDENT_STRING)
        newline = or_if_none(kwargs.get('newline'), DEFAULT_NEWLINE)
        encoding = or_if_none(kwargs.get('encoding'), DEFAULT_ENCODING)
        template_name = or_if_none(kwargs.get('template_name'), DEFAULT_TEMPLATE_NAME)

        self.structure = structure
        self.io = io
        self.indent_string = indent_string.encode(encoding)
        self.newline = newline.encode(encoding)
        self.encoding = encoding
        self.template_name = template_name
        self.class_name = utils.camel(template_name)

        # What to autoclose in case of return, break or continue statements
        # For returns
        self.func_stack = []
        # For continues and breaks
        self.loop_stack = []
        # Whether we're in the process of autoclosing nodes
        self.autoclosing_now = False

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

        for arg in args:
            if self.indent_level:
                self.io.write(indent_level * self.indent_string)
            self.io.write(arg.encode(self.encoding))
            self.io.write(self.newline)
    
    def write_file_header(self):
        self.write_io(
            '# -*- coding: {} -*-'.format(self.encoding),
        )

    def write_class(self):
        self.write_io(
            'template_class_name = ' + repr(self.class_name),
            'class {}({}):'.format(
                self.class_name,
                self.superclass_name,
            ),
        )
        self.indent()
        self.write_io(
            'encoding = {}'.format(repr(self.encoding)),
            '',
        )

    def write_imports(self):
        self.write_io(
            *self.imports
        )

    def open_template_function(self, name):
        self.write_io(
            'def {}(self, context):'.format(name),
        )
        self.indent()
        self.write_io(
            'with _ph_encapsulate_exceptions():',
        )
        self.autoclose_open_func()
        self.indent()

    def close_template_function(self):
        self.dedent(2)

    def write_root_node(self, node):
        # In this case as "root node" we mean node which has tree root as parent
        iter_stack = list()
        node_stack = list()
        current_iter = utils.one_iter(node)

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

    def write_structure(self):
        code_level = 0
        for node in self.structure:
            if code_level == 0 and not isinstance(node, structure.ModuleLevel):
                self.write_class()
                code_level = 1

            if code_level == 1 and not isinstance(node, structure.ClassLevel):
                self.open_template_function('body')
                code_level = 2

            self.write_root_node(node)

    def write(self):
        self.write_file_header()
        self.write_imports()
        self.write_structure()

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

    def handle_open_simple_statement(self, node):
        if node.name == 'return':
            log.debug('CLOSING FUNC')
            self.autoclose_close_func()
            log.debug('CLOSED FUNC')
        elif node.name in ('break', 'continue'):
            log.debug('CLOSING LOOP')
            self.autoclose_close_loop()
            log.debug('CLOSED LOOP')
        self.write_io(
            node.content,
        )
        if node.name in ('return', 'break', 'continue'):
            self.ignore_code_level = self.indent_level

    def handle_open_compound_statement(self, node):
        self.write_io(
            node.content,
        )
        # TODO: support def (when we start to understand it as CompoundStatement)
        if node.name in ('for', 'while'):
            log.debug('OPENING LOOP')
            self.autoclose_open_loop()

    def handle_close_compound_statement(self, node):
        # TODO: support def (when we start to understand it as CompoundStatement)
        if node.name in ('for', 'while'):
            log.debug('OPENING LOOP')
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

