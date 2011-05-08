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

def merge_element_attributes(id_, classes, attributes_set):
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

def prepare_for_tag(name, attributes):
    name = attributes.pop('_tag_name', name) or 'div'
    attributes = {
        key: (
            ' '.join(value)
            if (key == 'class' and not isinstance(value, str)) else
            value
        )
        for key, value in attributes.items()
        if not (
            key.startswith('_') or
            (key in ('id', 'class') and not value) or
            value in (None, False)
        )
    }
    return name, attributes

class Template:
    pass

