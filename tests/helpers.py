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

import logging
from unittest import TestCase

from pyhaa import (
    PyhaaEnvironment,
    PyhaaSyntaxError,
    SYNTAX_INFO,
)
from pyhaa.utils.cgrt_common import prepare_for_tag as pft

log = logging.getLogger(__name__)

def jl(*args):
    '''
    Simple helper to join lines
    '''
    return '\n'.join(args)

class PyhaaTestCase(TestCase):
    '''
    Extended TestCase for internal use
    '''

    def setUp(self):
        self.senv = PyhaaEnvironment()

    def assertPSE(self, _eid, _func, *args, **kwargs):
        '''
        PSE is short of PyhaaSyntaxError... It is too long so I abbreviated it
        _eid is expected PyhaaSyntacError type
        Returns caught exception for further assertions
        '''
        _eid = getattr(SYNTAX_INFO, _eid)
        try:
            _func(*args, **kwargs)
        except PyhaaSyntaxError as e:
            log.debug('Got exception: %s', str(e) )
            self.assertEqual(e.eid, _eid)
            # We may want to check further details
            return e
        self.fail('No expected exception raised')

    def assertAttributesEqual(self, tag, attributes):
        _, tag_attributes = pft(None, None, None, (
            (
                eval(value)
                if isinstance(value, str) else
                value
            )
            for value in tag.attributes_set
        ))
        self.assertDictEqual(
            tag_attributes,
            attributes,
        )

    #if not hasattr(TestCase, 'assertIsInstance'):
    # TODO?

