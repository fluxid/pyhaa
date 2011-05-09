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

from .encode import recursive_encode

def prepare_for_tag(name, id_, classes, attributes_set, do_byte_encode = False, do_entity_encode = False, encoding = 'utf-8'):
    (
        name,
        id_,
        classes,
        attributes_set,
    ) = recursive_encode(
        (
            name,
            id_,
            classes,
            attributes_set,
        ),
        do_byte_encode,
        do_entity_encode,
        encoding
    )

    # /r/ing better idea, because this one sucks a bit
    if do_byte_encode:
        x_ = b'_'
        x_append_class = b'_append_class'
        x_class = b'class'
        x_div = b'div'
        x_id = b'id'
        x_remove_class = b'_remove_class'
        x_sp = b' '
        x_tag_name = b'_tag_name'
        x_type = bytes
    else:
        x_ = '_'
        x_append_class = '_append_class'
        x_class = 'class'
        x_div = 'div'
        x_id = 'id'
        x_remove_class = '_remove_class'
        x_sp = ' '
        x_tag_name = '_tag_name'
        x_type = str

    def class_split_set(value):
        if value and isinstance(value, x_type):
            value = (
                sval
                for sval in value.split(x_sp)
                if sval
            )
        return set(value) if value else set()

    result = dict()
    classes = class_split_set(classes)

    for obj in attributes_set:
        if x_class in obj:
            classes = class_split_set(obj.pop(x_class, None))

        id_ = obj.pop(x_id, id_)
        name = obj.pop(x_tag_name, name)

        result.update((
            (key, value)
            for key, value in obj.items()
            if not (
                key.startswith(x_) or
                value in (False, None)
            )
        ))

        append = obj.get(x_append_class)
        if append:
            classes |= class_split_set(append)

        remove = obj.get(x_remove_class)
        if remove:
            classes -= class_split_set(remove)

    if classes:
        result[x_class] = x_sp.join(classes)

    if id_:
        result[x_id] = id_

    name = name or x_div
    return name, result

def open_tag(name, attributes, self_close):
    yield b'<'
    yield name
    for key, value in attributes.items():
        if value is True:
            value = key

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
    yield name
    yield b'>'

