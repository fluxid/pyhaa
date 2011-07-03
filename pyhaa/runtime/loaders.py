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
import posixpath

from ..utils import try_detect_encoding

class BaseLoader:
    def __init__(self, cache = None, check_time = True):
        self.cache = cache or {}
        self.check_time = check_time

    def load(self, path, environment, current_path = None):
        if current_path and not path.startswith('/'):
            path = posixpath.join(current_path, path)

        path = posixpath.normpath(path)

        if path.startswith('/'):
            path = path[1:]
        if path.startswith('..'):
            # TODO Raise proper exception
            raise Exception

        # TODO Move all the above to utils
        # TODO threadlocks

        if self.cache:
            cached = True
            if check_time:
                cache_time = self.cache.get_time(path, environment)
                loader_time = self.get_time(path, environment)
                if not cache_time or loader_time and cache_time < loader_time:
                    cached = False

            if cached:
                module = self.cache.get_module(path, environment)
                if module:
                    return module

        module = self.get_module(path, environment)
        if self.cache:
            self.cache.memorize(path, module, environment)

        return module

    def get_module(self, path, environment):
        raise NotImplementedError

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

    def get_filepath(self, path):
        path = os.path.normpath(path)
        for curpath in self.paths:
            curpath = os.path.join(curpath, path)
            if os.path.isfile(curpath):
                return curpath
        return None

    def get_time(self, path, environment):
        path = self.get_filepath(path)
        if not path:
            return None
        return os.path.getmtime(path)

    def get_module(self, path, environment):
        encoding = self.input_encoding
        our_path = self.get_filepath(path)
        if not our_path:
            # TODO raise proper exception
            raise Exception('File not found: "{}"'.format(path))
        with open(our_path, 'br') as fp:
            if not encoding:
                encoding = try_detect_encoding(fp) or 'utf-8'
            cfp = codecs.getreader(encoding)(fp)

            structure = environment.parse_io(cfp)
            code = environment.codegen_template(structure)
            return environment.compile_template(code)

