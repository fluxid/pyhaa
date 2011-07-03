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

import codecs
import os.path

from .cache import TemplateCache
from ..utils import try_detect_encoding

class BaseLoader:
    def __init__(self, template_cache_size = 100, bytecode_cache = None):
        self.template_cache = TemplateCache(template_cache_size)
        self.bytecode_cache = bytecode_cache

    def get_template_module(self, path, environment):
        template = self.template_cache.get(path)
        expired = None
        if template:
            template, token = template
            expired = self._is_expired(path, environment, token)
            if expired:
                self.template_cache.remove(path)
            else:
                return template

        bytecode = None
        read_from_cache = False
        if not expired and self.bytecode_cache:
            bytecode = self.bytecode_cache.get(path)
            if bytecode:
                bytecode, token = bytecode
                expired = self._is_expired(path, environment, token)
                if expired:
                    self.bytecode_cache.remove(path)
                    bytecode = None
                else:
                    read_from_cache = True

        if not bytecode:
            bytecode, token = self.get_bytecode(path, environment)

        template = environment.template_module_from_bytecode(bytecode)

        self.template_cache.store(path, (template, token))
        if not read_from_cache and self.bytecode_cache:
            self.bytecode_cache.store(path, bytecode, token) 

        return template

    def get_bytecode(self, path, environment):
        result, filename, token = self.get_python_code(path, environment)
        bytecode = compile(result, filename, 'exec')
        return bytecode, token

    def get_python_code(self, path, environment):
        result, filename, token = self.get_source_code(path, environment)
        structure = environment.parse_any(result)
        code = environment.codegen_structure(structure)
        return code, filename, token
    
    def get_source_code(self, path, environment):
        raise NotImplementedError

    def _is_expired(self, path, environment, token):
        if not environment.auto_reload:
            return False
        return self.is_expired(path, environment, token)

    def is_expired(self, path, environment, token):
        return False


class FileSystemLoader(BaseLoader):
    def __init__(self, paths = None, input_encoding = None, **kwargs):
        super().__init__(**kwargs)

        paths = [paths] if isinstance(paths, str) else paths
        paths = [
            os.path.realpath(os.path.expanduser(curpath))
            for curpath in paths
        ]
        # TODO check if paths are overlapping
        self.paths = paths
        self.input_encoding = input_encoding

    def lookup_filename(self, path):
        path = os.path.normpath(path)
        for curpath in self.paths:
            curpath = os.path.join(curpath, path)
            if os.path.isfile(curpath):
                return curpath
        return None

    def get_source_code(self, path, environment):
        encoding = self.input_encoding
        our_path = self.lookup_filename(path)
        if not our_path:
            # TODO raise proper exception
            raise Exception('Template not found: "{}"'.format(path))
        
        token = os.path.getmtime(our_path)

        fp = open(our_path, 'br')
        if not encoding:
            encoding = try_detect_encoding(fp) or 'utf-8'
        cfp = codecs.getreader(encoding)(fp)

        return cfp, our_path, token

    def is_expired(self, path, environment, token):
        our_path = self.lookup_filename(path)
        if not our_path:
            return True
        token2 = os.path.getmtime(our_path)
        return token2 > token

