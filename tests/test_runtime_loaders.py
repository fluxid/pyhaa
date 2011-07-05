# -*- coding: utf-8 -*-

'''
Testing template loading from files
'''

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

from unittest import TestCase
import os
import os.path
import tempfile

from pyhaa import (
    html_render_to_string,
    PyhaaEnvironment,
)
from pyhaa.runtime.loaders import FilesystemLoader

class TestLoaders(TestCase):
    def _load_and_render(self, environment, path, current_path = None):
        template = environment.get_template(path, current_path)
        return html_render_to_string(template)

    def test_basic_load_and_render(self):
        loader = FilesystemLoader(paths='./tests/files/', input_encoding = 'utf-8')
        environment = PyhaaEnvironment(loader = loader)
        rendered = self._load_and_render(environment, 'basic.pha')
        self.assertEqual(
            rendered,
            '<h1>ME GUSTA</h1>',
        )

    def test_lookup(self):
        paths = (
            './tests/files/lookup_tests/secondary',
            './tests/files/lookup_tests/main',
        )
        loader = FilesystemLoader(paths=paths, input_encoding='utf-8')
        environment = PyhaaEnvironment(loader=loader)

        rendered = self._load_and_render(environment, 'common/parts/first.pha')
        self.assertEqual(rendered, 'secondary!')

        # For example, we use second.pha inside first.pha - relative path
        rendered = self._load_and_render(environment, 'second.pha', 'common/parts/')
        self.assertEqual(rendered, 'second not secondary!')

        # Now get something using absolute path
        rendered = self._load_and_render(environment, '/root.pha', 'common/parts/')
        self.assertEqual(rendered, 'secondary root!')

        # Now get something using absolute path
        rendered = self._load_and_render(environment, '../../pages/page.pha', 'common/parts/')
        self.assertEqual(rendered, 'I am the page!')

    def test_reload(self):
        reloaded = False

        class MyLoader(FilesystemLoader):
            def get_bytecode(self, *args, **kwargs):
                nonlocal reloaded
                reloaded = True
                return super().get_bytecode(*args, **kwargs)

        loader = MyLoader(paths='./tests/files/', input_encoding = 'utf-8')
        environment = PyhaaEnvironment(loader = loader)

        self._load_and_render(environment, 'basic.pha')
        reloaded = False
        self._load_and_render(environment, 'basic.pha')
        self.assertFalse(reloaded)
        os.utime('./tests/files/basic.pha', None)
        self._load_and_render(environment, 'basic.pha')
        self.assertTrue(reloaded)
        reloaded = False
        environment.auto_reload = False
        os.utime('./tests/files/basic.pha', None)
        self._load_and_render(environment, 'basic.pha')
        self.assertFalse(reloaded)

    def test_reload_on_path_change(self):
        '''
        Case: We have two paths. Template is in second.
        After we load this template for the first time, we move
        file from other location to the first one.
        New template overlays the already loaded one - it would
        match the same path.
        Because we move file, its mtime may be older than mtime
        of the already loaded one.
        We should detect new file an reload template.
        '''
        tmpdir = tempfile.mkdtemp(dir='.')
        try:
            paths = (
                tmpdir,
                './tests/files/',
            )
            loader = FilesystemLoader(paths=paths, input_encoding='utf-8')
            environment = PyhaaEnvironment(loader = loader)

            self.assertEqual(
                self._load_and_render(environment, 'basic.pha'),
                '<h1>ME GUSTA</h1>',
            )

            tmpfile = os.path.join(tmpdir, 'basic.pha')
            try:
                with open(tmpfile, 'w') as fp:
                    fp.write('%strong reload!')

                # Make sure file from first path is actually older
                # Otherwise it happily reloads because of mtime change
                # But it must reload because of different path/new file
                os.utime('./tests/files/basic.pha', None)
                newtime = os.path.getmtime(tmpfile) - 100
                os.utime(tmpfile, (newtime, newtime))

                self.assertEqual(
                    self._load_and_render(environment, 'basic.pha'),
                    '<strong>reload!</strong>',
                )
            finally:
                os.remove(tmpfile)

            environment.auto_reload = False
            self.assertEqual(
                self._load_and_render(environment, 'basic.pha'),
                '<strong>reload!</strong>',
            )
            environment.auto_reload = True
            self.assertEqual(
                self._load_and_render(environment, 'basic.pha'),
                '<h1>ME GUSTA</h1>',
            )
        finally:
            os.rmdir(tmpdir)


