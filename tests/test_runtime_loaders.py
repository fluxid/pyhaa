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

from pyhaa import (
    html_render_to_string,
    PyhaaEnvironment,
)
from pyhaa.runtime.loaders import FileSystemLoader

class TestLoaders(TestCase):
    def test_basic_load_and_render(self):
        loader = FileSystemLoader(paths='./tests/files/', input_encoding = 'utf-8')
        environment = PyhaaEnvironment(loader = loader)
        template = environment.get_template('basic.pha')
        rendered = html_render_to_string(template)
        self.assertEqual(
            rendered,
            '<h1>ME GUSTA</h1>',
        )

