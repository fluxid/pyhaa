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

from ..utils.cgrt_common import (
    close_tag,
    open_tag,
    prepare_for_tag,
)

def _ph_open_tag(tag_name_stack, name, id_, classes, attributes, self_close, encoding):
    name, attributes = prepare_for_tag(name, id_, classes, attributes, True, True, encoding)
    if not self_close:
        tag_name_stack.append(name)
    return open_tag(name, attributes, self_close)

def _ph_close_tag(tag_name_stack):
    return close_tag(tag_name_stack.pop())

