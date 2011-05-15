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

        self.indent_level = 0

    def indent(self):
        self.indent_level += 1

    def dedent(self, times=1):
        if self.indent_level and times:
            self.indent_level -= min(times, self.indent_level)

    def write_io(self, *args):
        for arg in args:
            if self.indent_level:
                self.io.write(self.indent_level * self.indent_string)
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

    def write_template_function(self, name):
        self.write_io(
            'def {}(self, context):'.format(name),
        )
        self.indent()

    def write_root_node(self, node):
        # In this case as "root node" we mean node which has tree root as parent
        iter_stack = list()
        node_stack = list()
        current_iter = utils.one_iter(node)

        while True:
            node = next(current_iter, None)
            if node is None:
                if node_stack:
                    self.call_node_handling_function('close', node_stack.pop())
                if not iter_stack:
                    while node_stack:
                        self.call_node_handling_function('close', node_stack.pop())
                    break
                current_iter = iter_stack.pop()
                continue

            self.call_node_handling_function('open', node)
            if isinstance(node, structure.PyhaaParent):
                node_stack.append(node)
                iter_stack.append(current_iter)
                current_iter = iter(node)
            else:
                self.call_node_handling_function('close', node)

    def write_structure(self):
        code_level = 0
        for node in self.structure:
            if code_level == 0 and not isinstance(node, structure.ModuleLevel):
                self.write_class()
                code_level = 1

            if code_level == 1 and not isinstance(node, structure.ClassLevel):
                self.write_template_function('body')
                code_level = 2

            self.write_root_node(node)

    def write(self):
        self.write_file_header()
        self.write_imports()
        self.write_structure()

    def call_node_handling_function(self, prefix, node):
        if node is None:
            return
        function_name = name_node_handling_function(prefix, node)
        function = getattr(self, function_name, None)
        if function:
            function(node)
        else:
            log.warning("Couldn't find function %s for node %r.", function_name, node)

