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

from pyhaa.utils import encode

from .helpers import PyhaaTestCase

class TestUtilsEncode(PyhaaTestCase):
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

    def test_recursive_encode(self):
        self.assertEqual(
            encode.recursive_encode(('<aaa>', b'<bbb>', None, 12, ['ccc'], {'ddd'}, {'eee':'fff'})),
            (b'<aaa>', b'<bbb>', None, 12, [b'ccc'], {b'ddd'}, {b'eee':b'fff'})
        )
        self.assertEqual(
            encode.recursive_encode(('<aaa>', b'<bbb>', None, 12, ['ccc'], {'ddd'}, {'eee':'fff'}), False),
            ('<aaa>', b'<bbb>', None, 12, ['ccc'], {'ddd'}, {'eee':'fff'})
        )
        self.assertEqual(
            encode.recursive_encode(('<aaa>', b'<bbb>', None, 12, ['ccc'], {'ddd'}, {'eee':'fff'}), False, True),
            ('&lt;aaa&gt;', b'<bbb>', None, 12, ['ccc'], {'ddd'}, {'eee':'fff'})
        )
        self.assertEqual(
            encode.recursive_encode(('<aaa>', b'<bbb>', None, 12, ['ccc'], {'ddd'}, {'eee':'fff'}), True, True),
            (b'&lt;aaa&gt;', b'<bbb>', None, 12, [b'ccc'], {b'ddd'}, {b'eee':b'fff'})
        )

    def test_single_encode(self):
        self.assertEqual(
            encode.single_encode(None),
            None,
        )
        self.assertEqual(
            encode.single_encode(12),
            12,
        )
        self.assertEqual(
            encode.single_encode('abc'),
            b'abc',
        )
        self.assertEqual(
            encode.single_encode('abc', False),
            'abc',
        )
        self.assertEqual(
            encode.single_encode('<abc>', False, True),
            '&lt;abc&gt;',
        )
        self.assertEqual(
            encode.single_encode('<abc>', True, True),
            b'&lt;abc&gt;',
        )
        self.assertEqual(
            encode.single_encode('zażółć', encoding='iso-8859-2'),
            'zażółć'.encode('iso-8859-2'),
        )
        self.assertEqual(
            encode.single_encode('zażółć', encoding='utf8'),
            'zażółć'.encode('utf8'),
        )
        self.assertEqual(
            encode.single_encode(None, stringify=True),
            b'None',
        )
        self.assertEqual(
            encode.single_encode(12, stringify=True),
            b'12',
        )
        self.assertEqual(
            encode.single_encode(b'<abc>', True, True, stringify=True),
            b'<abc>',
        )

    def test_single_encode_generators(self):
        def gen1():
            yield b'hurr<>durr'
        def gen2():
            yield 12
            yield '<abc>'
            yield gen1()

        self.assertTrue(isinstance(
            encode.single_encode(gen2(), True, True, allow_generators=False, stringify=True),
            bytes
        ))
        self.assertSequenceEqual(
            list(encode.single_encode(gen2(), True, True, allow_generators=True, stringify=True)),
            [b'12', b'&lt;abc&gt;', b'hurr<>durr'],
        )



