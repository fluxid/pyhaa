# -*- coding: utf-8 -*-

'''
Test HTML code generation
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

import io
from unittest import TestCase

from pyhaa import (
    parse_string,
)
from pyhaa.codegen.html import HTMLCodeGen

from .helpers import jl

class TestBasics(TestCase):
    def test_basic_codegen(self):
        tree = parse_string(jl(
            '%a',
            '  %b to jest jakiś tekst...',
            '%c(a)',
            '%br',
            '%div#im_so_dynamic(value="notlol"){"value":lol, "id":"cool effects of being dynamic"}',
            '%label',
            '  This looks cool!',
            '  %input.text_box(type=text){"value":form.fields[0].value}',
        ))
        bio = io.BytesIO()
        cg = HTMLCodeGen(tree, bio)
        cg.write()
        print(bio.getvalue().decode('utf-8'))

