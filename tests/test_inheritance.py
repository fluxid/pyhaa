# -*- coding: utf-8 -*-

'''
Test template inheritance
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
    def setUp(self):
        loader = FilesystemLoader(paths='./tests/files/inheritance', input_encoding = 'utf-8')
        self.environment = PyhaaEnvironment(loader = loader)

    def _load_and_render(self, path):
        template = self.environment.get_template(path)
        return html_render_to_string(template)

    def test_basic_inheritance(self):
        self.assertEqual(
            self._load_and_render('basic_A.pha'),
            'A B',
        )

    def test_complicated_inheritance(self):
        #       A
        #       |
        #     +-+-+
        #     |   |
        #     B   C
        #     |   |
        #   +-+---|--+
        #   |     |  |
        #   D     |  |
        #   |     |  |
        #   +---+-+--+
        #       |
        #       E ← (E inherits, in order, from D, C and B)
        # Notice inherit syntax in E is split in two lines to test if it works...
        self.assertEqual(
            self._load_and_render('comp_E.pha'),
            'E D C B A',
        )

    def test_loop_detect_short(self):
        self.assertRaises(
            Exception,
            self._load_and_render,
            'loop_A.pha',
        )

    def test_loop_detect_long(self):
        self.assertRaises(
            Exception,
            self._load_and_render,
            'loop2_A.pha',
        )

