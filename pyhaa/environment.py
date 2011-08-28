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
import posixpath

from .utils import sequence_flatten
from .runtime.proxy import InstanceProxy

__all__ = (
    'PyhaaEnvironment',
)

class PyhaaEnvironment:
    def __init__(
        self,
        loader=None,
        parser_class=None,
        codegen_class=None,
        output_encoding='utf-8',
        auto_reload = True,
    ):
        if not parser_class:
            from .parsing.parser import PyhaaParser
            parser_class = PyhaaParser

        if not codegen_class:
            from .codegen.html import HTMLCodeGen
            codegen_class = HTMLCodeGen

        self.loader = loader
        self.parser_class = parser_class
        self.codegen_class = codegen_class
        self.output_encoding = output_encoding
        self.auto_reload = auto_reload

    def get_template_info(self, path, current_path=None):
        if current_path and not path.startswith('/'):
            path = posixpath.join(current_path, path)

        path = posixpath.normpath(path)

        if path.startswith('/'):
            path = path[1:]
        if path.startswith('..'):
            # TODO Raise proper exception
            raise Exception

        return self.loader.get_template_info(path, self)

    def get_inheritance_chain(self, template_info):
        '''
        Returns "teplate precedence list"
        Inheritance linearization works as in C3 algorithm, used in Python itself.
        '''
        templates = dict()
        onpath = set()

        def in_tail(what, where, whence):
            try:
                return where.index(what) > whence
            except ValueError:
                return False

        def merge_inheritance(list_):
            # Do as in cpython's typeobject.c - store positions, don't pop from lists
            positions = [0]*len(list_)
            empty = 0
            cont = True
            while cont:
                cont = False
                for idx, lst in enumerate(list_):
                    pos = positions[idx]

                    # Check if list is empty
                    if pos >= len(lst):
                        # it's empty
                        empty += 1
                        continue

                    head = lst[pos]

                    # check if candidate is in tail of any of the lists
                    found_tail = False
                    for lst in list_:
                        if in_tail(head, lst, pos):
                            found_tail = True
                            break
                    if found_tail:
                        continue
                    
                    # yield it to line
                    yield head

                    # remove candidate from heads
                    for idx, lst in enumerate(list_):
                        pos = positions[idx]
                        if pos < len(lst) and lst[pos] == head:
                            positions[idx] = pos + 1

                    cont = True
                    break

            if empty == len(list_):
                # OK, we emptied all the lists
                return
            raise Exception('Failed to resolve inheritance precedence')

        def load_inheritance(template_info):
            inheritance = [template_info]
            parents = templates[template_info]
            if not parents:
                return inheritance
            loaded = [
                load_inheritance(pinfo)
                for pinfo in parents
            ]
            loaded.append(parents)
            inheritance.extend(merge_inheritance(loaded))
            return inheritance

        def load_template_infos(template_info):
            onpath.add(template_info)
            parents = []
            for ppath in sequence_flatten(template_info.inheritance()):
                # TODO Include current path!!!
                parent = self.get_template_info(ppath) # , current_path = template_info['path']) or smth

                if parent in onpath:
                    raise Exception('Loop detected in inheritance tree!')

                if parent not in templates:
                    load_template_infos(parent)

                parents.append(parent)
            templates[template_info] = parents
            onpath.remove(template_info)

        # Load all templates in inheritance tree
        load_template_infos(template_info)
        return load_inheritance(template_info)

    def get_template(self, path, current_path=None):
        '''
        Returns template instance along with complete parent chain
        '''
        template_info = self.get_template_info(path, current_path)
        linearized = self.get_inheritance_chain(template_info)
        print(linearized)
        return InstanceProxy(linearized, self)

    def parse_readline(self, readline):
        parser = self.parser_class()
        parser.parse_readline(readline)
        parser.finish()
        return parser.structure

    def parse_io(self, fp):
        result = self.parse_readline(fp.readline)
        fp.close()
        return result

    def parse_string(self, string):
        return self.parse_io(io.StringIO(string))

    def parse_any(self, source):
        if isinstance(source, io.IOBase) or hasattr(source, 'readline'):
            return self.parse_io(source)

        if isinstance(source, str):
            return self.parse_string(source)

        if hasattr(source, '__call__'):
            return self.parse_readline(source)

        # TODO - And do we need it?
        #if hasattr(source, '__next__'): #iter2readline(source)
        #if hasattr(source, '__iter__'): #iter2readline(iter(source))

    def codegen_structure(self, structure, **kwargs):
        bio = io.BytesIO()
        kwargs.setdefault('encoding', self.output_encoding)
        cg = self.codegen_class(structure, bio, **kwargs)
        cg.write()
        return bio.getvalue()

    def template_info_from_bytecode(self, bytecode):
        dict_ = dict()
        exec(bytecode, dict_, dict_)
        return dict_['_ph_template_info']

