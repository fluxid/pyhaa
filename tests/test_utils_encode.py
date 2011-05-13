# -*- coding: utf-8 -*-

'''
Utility testing
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

from pyhaa.utils import encode

class TestEntities(TestCase):
    def test_encoding_basic(self):
        self.assertEqual(
            encode.entity_encode('<a href="#">\'oh&nbsp;wow\'</a>'),
            '&lt;a href=&quot;#&quot;&gt;&apos;oh&amp;nbsp;wow&apos;&lt;/a&gt;'
        )

    def test_decoding_basic(self):
        self.assertEqual(
            encode.entity_decode('&lt;a href=&quot;#&quot;&gt;&apos;oh&amp;nbsp;wow&apos;&lt;/a&gt;'),
            '<a href="#">\'oh&nbsp;wow\'</a>',
        )

    def test_decoding_aacute(self):
        self.assertEqual(
            encode.entity_decode('&Aacute;&#0000193;&#193;&#x000c1;&#xc1;\u00c1'),
            chr(193) * 6,
        )

