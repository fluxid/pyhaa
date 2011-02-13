# -*- coding: utf-8 -*-

class PyhaaParent:
    def __init__(self, **kwargs):
        self.children = list()
        self.root = self
        super().__init__(**kwargs)

    def append(self, other):
        other.root = self.root
        other.parent = self
        if self.children:
            last = self.children[-1]
            last.next_sibling = other
            other.prev_sibling = last
        self.children.append(other)
        return self
    
    def __iter__(self):
        return iter(self.children)


class PyhaaTree(PyhaaParent):
    def __init__(self):
        self.current = self
        super().__init__()

    def append(self, other):
        if self.current is self:
            super().append(other)
        else:
            self.current.append(other)
        self.current = other

    def close(self, times = 1):
        for i in range(times):
            if self.current is not self:
                self.current = self.current.parent


class PyhaaElement:
    def __init__(self, ws_out_left = True, ws_out_right = True):
        self.parent = None
        self.root = None
        self.prev_sibling = None
        self.next_sibling = None
        self.ws_out_left = ws_out_left
        self.ws_out_right = ws_out_right

    def append(self, other):
        raise Exception("Can\'t append children to normal element")

    #def get_indent_after(self):
    #    pass

    #def space_after(self):
    #    if self.sibling:
    #        # our outer right and one next to us outer left
    #        # ...</div><div>...
    #        return self.ws_out_right and self.sibling.ws_out_left
    #    if self.parent:
    #        # our outer right and parent's inner right
    #        # ...</div></div>
    #        return self.ws_out_right and self.parent.ws_in_right
    #    # We have no next sibling and no parent
    #    return False


class PyhaaElementOpenable(PyhaaParent, PyhaaElement):
    def __init__(self, ws_in_left = True, ws_in_right = True, **kwargs):
        self.ws_in_left = ws_in_left
        self.ws_in_right = ws_in_right
        super().__init__(**kwargs)

    #def space_after_opening(self):
    #    if self.children:
    #        # We take our inner left and outer left of the first child
    #        # <div><div>...
    #        return self.ws_in_left and self.children[0].ws_out_left
    #    # We're empty, so don't put anything inside
    #    # <div></div>
    #    return False

    #def get_indent_after_opening(self):
    #    return self.get_indent_after()

    #def get_indent_before_closing(self):
    #    pass

    #def space_after_closing(self):
    #    return self.space_after()


class Tag(PyhaaElementOpenable):
    def __init__(self, name = None, id_ = None, classes = None, simple_attributes = None, python_attributes = None, **kwargs):
        self._classes = None
        self._simple_attributes = None
        self._python_attributes = None

        self.name = name
        self.id_ = id_
        self.classes = classes
        self.simple_attributes = simple_attributes
        self.python_attributes = python_attributes
        super().__init__(**kwargs)

    def _get_classes(self):
        return self._classes

    def _set_classes(self, value):
        self._classes = set(value) if value else set()

    classes = property(_get_classes, _set_classes)

    def _get_simple_attributes(self):
        return self._simple_attributes

    def _set_simple_attributes(self, value):
        self._simple_attributes = dict(value) if value else dict()

    simple_attributes = property(_get_simple_attributes, _set_simple_attributes)

    def _get_python_attributes(self):
        return self._python_attributes

    def _set_python_attributes(self, value):
        if not value or value == '{}':
            value = None
        self._python_attributes = value

    python_attributes = property(_get_python_attributes, _set_python_attributes)


class Text(PyhaaElement):
    def __init__(self, text = None, escape = True, **kwargs):
        self.text = text
        self.escape = escape
        super().__init__(**kwargs)

