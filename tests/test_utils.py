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

import codecs
import io
from unittest import TestCase

from pyhaa import utils

class TestUtils(TestCase):
    def test_decamel(self):
        self.assertEqual(utils.decamel('CodeGen'), '_code_gen')

    def test_camel(self):
        self.assertEqual(utils.camel('code_gen'), 'CodeGen')
        self.assertEqual(utils.camel('_code_gen'), 'CodeGen')

    def _test_bom(self, bom, encoding):
        test_string = 'Zażółć gęślą jaźń'
        test_io = io.BytesIO(bom + test_string.encode(encoding))
        detected_encoding = utils.try_detect_encoding(test_io)
        self.assertEqual(codecs.lookup(detected_encoding), codecs.lookup(encoding))
        decoded = codecs.getreader(detected_encoding)(test_io).read()
        self.assertEqual(decoded, test_string)

    def _test_magic(self, encoding):
        test_string = 'Zażółć gęślą jaźń'
        magic = '; -*- coding: {} -*-\n'.format(encoding)
        # Magic comment must be included in resulting stream!
        test_string = magic + test_string 
        test_io = io.BytesIO(test_string.encode(encoding))
        detected_encoding = utils.try_detect_encoding(test_io)
        self.assertEqual(codecs.lookup(detected_encoding), codecs.lookup(encoding))
        decoded = codecs.getreader(detected_encoding)(test_io).read()
        self.assertEqual(decoded, test_string)

    def test_try_detect_encoding(self):
        self._test_bom(codecs.BOM_UTF8, 'utf8')
        self._test_bom(codecs.BOM_UTF16_LE, 'utf-16-le')
        self._test_bom(codecs.BOM_UTF16_BE, 'utf-16-be')
        self._test_bom(codecs.BOM_UTF32_LE, 'utf-32-le')
        self._test_bom(codecs.BOM_UTF32_BE, 'utf-32-be')
        self._test_magic('iso-8859-2')
        self._test_magic('utf-8')

