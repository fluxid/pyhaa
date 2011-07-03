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

import io

__all__ = (
    'PyhaaEnvironment',
)

class PyhaaEnvironment:
    def __init__(self, loader=None, parser_class=None, codegen_class=None, output_encoding='utf-8'):
        self.loader = loader
        self.parser_class = parser_class
        self.codegen_class = codegen_class
        self.output_encoding = output_encoding

    def get_parser_class(self):
        if self.parser_class:
            return self.parser_class

        from .parsing.parser import PyhaaParser
        return PyhaaParser

    def get_codegen_class(self):
        if self.codegen_class:
            return self.codegen_class

        from .codegen.html import HTMLCodeGen
        return HTMLCodeGen

    def get_template(self, path, current_path=None):
        assert self.loader
        return self.loader.load(path, self, current_path)

    def parse_readline(self, readline):
        parser = self.get_parser_class()()
        parser.parse_readline(readline)
        parser.finish()
        return parser.structure

    def parse_io(self, fp):
        return self.parse_readline(fp.readline)

    def parse_string(self, string):
        return self.parse_io(io.StringIO(string))

    def codegen_template(self, structure, **kwargs):
        bio = io.BytesIO()
        kwargs.setdefault('encoding', self.output_encoding)
        cg = self.get_codegen_class()(structure, bio, **kwargs)
        cg.write()
        return bio.getvalue()

    def compile_template(self, code):
        dict_ = dict()
        exec(code, dict_, dict_)
        template = dict_[dict_['template_class_name']]
        return template

