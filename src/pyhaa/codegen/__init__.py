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

from .. import structure

DEFAULT_INDENT = '    '
DEFAULT_NEWLINE = '\n'

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

    def write_node(self, node):
        raise NotImplementedError

    def write_structure(self):
        code_level = 0
        for node in self.structure:
            if code_level == 0 and not isinstance(node, structure.ModuleLevel):
                self.write_class()
                code_level = 1

            if code_level == 1 and not isinstance(node, structure.ClassLevel):
                self.write_template_function('body')
                code_level = 2

            self.write_node(node)

    def write(self):
        self.write_file_header()
        self.write_imports()
        self.write_structure()
