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

def merge_element_attributes(id_, classes, attributes_set, work_on_bytes = False, encoding = 'utf-8'):
    # /r/ing better idea, because this one sucks
    if work_on_bytes:
        x_tag_name = b'_tag_name'
        x_div = b'div'
        x_space = b' '
        x_class = b'class'
        x_id = b'id'
        x_ = b'_'
        x_type = bytes
    else:
        x_tag_name = '_tag_name'
        x_div = 'div'
        x_space = ' '
        x_class = 'class'
        x_id = 'id'
        x_ = '_'
        x_type = str

    result = {
        'id': id_,
        'class': list(classes) if classes else list(),
    }
    for obj in attributes_set:
        result.update(obj)
        classes = result['class']

        append = obj.get('_append_class')
        if append:
            if isinstance(append, str):
                append = [append]
            for class_ in append:
                if not class_ in classes:
                    classes.append(class_)

        remove = obj.get('_remove_class')
        if remove:
            if isinstance(remove, str):
                remove = [remove]
            for class_ in remove:
                if class_ in classes:
                    classes.remove(class_)

    return result

def prepare_for_tag(name, attributes, work_on_bytes = False):
    # /r/ing better idea, because this one sucks
    if work_on_bytes:
        x_tag_name = b'_tag_name'
        x_div = b'div'
        x_space = b' '
        x_class = b'class'
        x_id = b'id'
        x_ = b'_'
        x_type = bytes
    else:
        x_tag_name = '_tag_name'
        x_div = 'div'
        x_space = ' '
        x_class = 'class'
        x_id = 'id'
        x_ = '_'
        x_type = str

    name = attributes.pop(x_tag_name, name) or x_div
    attributes = {
        key: (
            x_sp.join(value)
            if (key == x_class and not isinstance(value, x_type)) else
            value
        )
        for key, value in attributes.items()
        if not (
            key.startswith(x_) or
            (key in (x_id, x_class) and not value) or
            value in (None, False)
        )
    }
    return name, attributes

class Template:
    pass

