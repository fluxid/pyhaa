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

class BoundPartial:
    def __init__(self, instance, parent, name, partial):
        self.instance = instance
        self.parent = parent
        self.name = name
        self.partial = partial

    def __call__(self, *args, **kwargs):
        return self.partial(self.instance, self.parent, *args, **kwargs)

    def __repr__(self):
        return '<{} {} {}>'.format(
            self.__class__.__name__,
            self.name,
            self.partial,
        )


class NamespaceLookup:
    def __getattr__(self, name):
        #if name.startswith('_ph_'):
        #    getattr(super(NamespaceLookup, self), name)
        try:
            result = getattr(self._ph_template, name)
        except AttributeError:
            pass
        else:
            return result

        partial = self._ph_template.get_partial(name)
        if partial:
            result = BoundPartial(self._ph_instance, self._ph_parent, name, partial)
            #import pdb; pdb.set_trace()
            return result
        if self._ph_parent:
            return getattr(self._ph_parent, name)

        # TODO Template X has no attribyte Y
        raise AttributeError(name)
    
    def __call__(self, *args, **kwargs):
        partial = getattr(self, '__body__')
        return partial(*args, **kwargs)


class ParentProxy(NamespaceLookup):
    __slots__ = ('_ph_instance', '_ph_template', '_ph_parent')

    def __init__(self, instance, template):
        self._ph_instance = instance
        self._ph_template = template
        self._ph_parent = None


class InstanceProxy(NamespaceLookup):
    def __init__(self, inheritance_chain, environment):
        iiter = iter(inheritance_chain)
        template = next(iiter)

        self._ph_instance = self
        self._ph_template = template
        self._ph_parent = None
        self._ph_environment = environment

        last_one = self
        for parent_template in iiter:
            last_one._ph_parent = parent = ParentProxy(self, parent_template)
            last_one = parent 
        #import pdb; pdb.set_trace()


    def __repr__(self):
        return '<{} {}>'.format(
            self.__class__.__name__,
            repr(self._ph_template),
        )

