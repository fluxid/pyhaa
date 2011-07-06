# -*- coding: utf-8 -*-

'''
Testing cache
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

import tempfile
import os

from unittest import TestCase

from pyhaa import (
    html_render_to_string,
    PyhaaEnvironment,
)
from pyhaa.runtime.cache import (
    FilesystemBytecodeCache,
    LFUCache,
)

from pyhaa.runtime.loaders import FilesystemLoader

class TestCache(TestCase):
    def test_template_cache(self):
        cache = LFUCache(2, 2)
        # template cache doesn't really care about what is stored in it
        cache.store('a', 'a!')
        cache.store('b', 'b!')
        cache.store('c', 'c!')
        cache.store('d', 'd!')
        self.assertEqual(cache.get('d'), 'd!')
        self.assertEqual(cache.get('a'), 'a!')
        self.assertEqual(cache.get('d'), 'd!')
        self.assertEqual(cache.get('a'), 'a!')
        self.assertEqual(cache.get('c'), 'c!')
        cache.store('e', 'e!')
        # In above call cache should be cleaned up
        # Correct guess are b (used once) and b (never used)
        self.assertEqual(cache.get('c'), None)
        self.assertEqual(cache.get('b'), None)
        self.assertEqual(cache.get('d'), 'd!')
        self.assertEqual(cache.get('a'), 'a!')
        self.assertEqual(cache.get('a'), 'a!')
        self.assertEqual(cache.get('e'), 'e!')
        self.assertEqual(cache.get('e'), 'e!')
        cache.store('f', 'f!')
        cache.store('g', 'g!')
        # f - zero uses. Sorry, it didn't make it
        self.assertEqual(cache.get('f'), None)
        # g was added after cleanup
        self.assertEqual(cache.get('g'), 'g!')
        # e had more (two) uses than f but got removed too
        self.assertEqual(cache.get('e'), None)
        # a and d still on top...
        self.assertEqual(cache.get('d'), 'd!')
        self.assertEqual(cache.get('a'), 'a!')

        # Duh, we shouldn't touch internals...
        self.assertEqual(cache.offset, 3)
        self.assertEqual(cache.cachedict['a'].priority, 5)
        self.assertEqual(cache.cachedict['d'].priority, 4)
        cache.reduce_offset()
        self.assertEqual(cache.offset, 0)
        self.assertEqual(cache.cachedict['a'].priority, 2)
        self.assertEqual(cache.cachedict['d'].priority, 1)

        cache.clear()
        self.assertEqual(cache.get('a'), None)

    def test_filesystem_bytecode_cache(self):
        reloaded = False

        class MyLoader(FilesystemLoader):
            def get_bytecode(self, *args, **kwargs):
                nonlocal reloaded
                reloaded = True
                return super().get_bytecode(*args, **kwargs)

        filenames = set()
        byte_loaded = False
        byte_stored = False

        class MyCache(FilesystemBytecodeCache):
            def get(self, *args, **kwargs):
                nonlocal byte_loaded
                result = super().get(*args, **kwargs)
                if result:
                    byte_loaded = True
                return result

            def store(self, *args, **kwargs):
                nonlocal byte_stored
                byte_stored = True
                return super().store(*args, **kwargs)

            def build_filename(self, *args, **kwargs):
                filename = super().build_filename(*args, **kwargs)
                filenames.add(filename)
                return filename

        tmpdir = tempfile.mkdtemp(dir='.')
        try:
            loader = MyLoader(paths='./tests/files/', bytecode_cache = MyCache(storage_directory=tmpdir), input_encoding = 'utf-8')
            environment = PyhaaEnvironment(loader = loader)

            def test_render():
                template = environment.get_template('basic.pha')
                self.assertEqual(
                    html_render_to_string(template),
                    '<h1>ME GUSTA</h1>',
                )

            test_render()
            self.assertTrue(byte_stored)
            self.assertEqual(len(filenames), 1)
            self.assertTrue(os.path.exists(list(filenames)[0]))
            # OK, we confirmed cache stored *something*

            reloaded = False
            byte_stored = False
            test_render()
            self.assertFalse(reloaded)
            self.assertFalse(byte_loaded)
            # Cool, we didn't reload - this means we loaded from LFUCache...
            # But...
            loader.template_cache.clear() # yuck, internals again

            test_render()
            self.assertFalse(reloaded)
            self.assertTrue(byte_loaded)
            self.assertFalse(byte_stored)
            # OK, we loaded from bytecache...
            self.assertEqual(len(filenames), 1)
            # And still, nothing changed... what about expiring?

            byte_loaded = False
            os.utime('./tests/files/basic.pha', None)
            test_render()
            # template cache returns expired token
            # we shouldn't even try to load bytecode cache if we know already it's expired...
            self.assertFalse(byte_loaded)
            # but we reload and store succesfully
            self.assertTrue(reloaded)
            self.assertTrue(byte_stored)

            reloaded = False
            byte_loaded = False
            byte_stored = False
            os.utime('./tests/files/basic.pha', None)
            loader.template_cache.clear() # don't use template cache at all this time
            test_render()
            # we load cache successfully ...
            self.assertTrue(byte_loaded)
            # ... but it ends up expired so we ...
            self.assertTrue(reloaded)
            # ... and store it again
            self.assertTrue(byte_stored)
        finally:
            for filename in filenames:
                os.remove(filename)
            os.rmdir(tmpdir)

