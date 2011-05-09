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

import re

from . import dict_sub

# TODO List all entities here
ENTITIES_DECODE = {
    'amp': '&',
    'quot': '"',
    'apos': "'",
    'lt': '<',
    'gt': '>',
}
RE_ENTITIES_ENCODE = re.compile('&([^\s;&]+);')

_ENCODEABLE = '&\'"<>'
_ENTITIES_ENCODE = {
    value: key
    for key, value in ENTITIES_DECODE.items()
}
ENTITIES_ENCODE = {
    character: (
        '&#{};'.format(ord(character))
        if entity is None else
        '&{};'.format(entity)
    )
    for character, entity in (
        (character, _ENTITIES_ENCODE.get(character))
        for character in _ENCODEABLE
    )
}
del _ENTITIES_ENCODE, _ENCODEABLE


entity_decode = dict_sub(ENTITIES_DECODE, RE_ENTITIES_ENCODE, 1)


entity_encode = dict_sub(ENTITIES_ENCODE)


def single_encode(value, do_byte_encode = True, do_entity_encode = False, encoding = 'utf-8'):
    if isinstance(value, str):
        if do_entity_encode:
            value = entity_encode(value)
        if do_byte_encode:
            value = value.encode(encoding, encoding)
    return value

def recursive_encode(value, do_byte_encode = True, do_entity_encode = False, encoding = 'utf-8'):
    # Of course, it doesn't cover all possibilities
    if isinstance(value, bytes) or not (do_byte_encode or do_entity_encode):
        return value

    if isinstance(value, dict):
        return {
            single_encode(key): recursive_encode(value, do_byte_encode, do_entity_encode, encoding)
            for key, value in value.items()
        }

    type_ = None
    if isinstance(value, set):
        type_ = set
    elif isinstance(value, (list, tuple)):
        type_ = list

    if not type_:
        return single_encode(value, do_byte_encode, do_entity_encode, encoding)
    
    return type_((
        recursive_encode(item, do_byte_encode, do_entity_encode, encoding)
        for item in value
    ))

