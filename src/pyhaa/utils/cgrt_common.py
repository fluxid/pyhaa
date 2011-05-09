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
        x_tag_name = b'_tag_name'
        x_div = b'div'
        x_space = b' '
        x_class = b'class'
        x_id = b'id'
        x_ = b'_'
        x_append_class = b'_append_class'
        x_remove_class = b'_remove_class'
        x_type = bytes
    else:
        x_tag_name = '_tag_name'
        x_div = 'div'
        x_space = ' '
        x_class = 'class'
        x_id = 'id'
        x_ = '_'
        x_append_class = '_append_class'
        x_remove_class = '_remove_class'
        x_type = str

    result = {
        x_id: id_,
        x_class: list(classes) if classes else list(),
    }
    for obj in attributes_set:
        result.update(obj)
        classes = result[x_class]

        append = obj.get(x_append_class)
        if append:
            if isinstance(append, x_type):
                append = [append]
            for class_ in append:
                if not class_ in classes:
                    classes.append(class_)

        remove = obj.get(x_remove_class)
        if remove:
            if isinstance(remove, x_type):
                remove = [remove]
            for class_ in remove:
                if class_ in classes:
                    classes.remove(class_)

    name = result.pop(x_tag_name, None) or x_div
    attributes = {
        key: (
            x_sp.join(value)
            if (key == x_class and not isinstance(value, x_type)) else
            value
        )
        for key, value in result.items()
        if not (
            key.startswith(x_) or
            (key in (x_id, x_class) and not value) or
            value in (None, False)
        )
    }
    return name, attributes

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

