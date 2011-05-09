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

import types

from ..utils import entity_encode

from . import (
    Template,
    merge_element_attributes,
    prepare_for_tag,
)

def selective_encode(value):
    if isinstance(value, bytes):
        return value
    return entity_encode(value).encode('utf-8')

def open_tag(name, attributes, self_close):
    yield b'<'
    yield selective_encode(name)
    for key, value in attributes.items():
        key = selective_encode(key)
        if value is True:
            value = key
        else:
            value = selective_encode(value)

        yield b' '
        yield key
        yield b'="'
        yield value
        yield b'"'
    if self_close:
        yield b' />'
    else:
        yield b'>'

def close_tag(name):
    yield b'</'
    yield selective_encode(name)
    yield b'>'


class HTMLTemplate(Template):
    def __init__(self, *args, **kwargs):
        self.tag_name_stack = list()

    def open_tag(self, name, id_, classes, attributes, self_close):
        name, attributes = prepare_for_tag(name, merge_element_attributes(id_, classes, attributes))
        if not self_close:
            self.tag_name_stack.append(name)
        return open_tag(name, attributes, self_close)

    def close_tag(self):
        return close_tag(self.tag_name_stack.pop())

