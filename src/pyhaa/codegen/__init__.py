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

DEFAULT_INDENT = '    '
DEFAULT_NEWLINE = '\n'

RE_DECAMEL = re.compile('[A-Z]')

log = logging.getLogger(__name__)

def decamel(string):
    def _decamel(match):
        return '_' + match.group(0).lower()
    # We're not removing '_' prefix
    return RE_DECAMEL.sub(_decamel, string)

def name_node_handling_function(prefix, node):
    return 'handle_' + prefix + decamel(node.__class__.__name__)

def byterepr(value):
    if isinstance(value, str):
        return repr(value.encode('utf-8'))
    return repr(value)


class CodeGen:
    superclass_name = 'Template'
    imports = (
        'from pyhaa.runtime import Template',
    )

    def __init__(self, structure, io, indent_string=DEFAULT_INDENT, newline=DEFAULT_NEWLINE):
        self.structure = structure
        self.io = io
        self.indent_string = indent_string.encode('utf-8')
        self.newline = newline.encode('utf-8')

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
            self.io.write(arg.encode('utf-8'))
            self.io.write(self.newline)
    
    def write_file_header(self):
        self.write_io(
            '# -*- coding: utf-8 -*-',
        )

    def write_class(self):
        self.write_io(
            'class ThisTemplate({}):'.format(self.superclass_name),
        )
        self.indent()

    def write_imports(self):
        self.write_io(
            *self.imports
        )

    def write_template_function(self, name):
        self.write_io(
            'def render_{}(self, **kwargs):'.format(name),
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

