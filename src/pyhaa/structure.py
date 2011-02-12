# -*- coding: utf-8 -*-

class PyhaaTree:
    def __init__(self):
        self.current = self
        self.children = list()
        self.prev_sibling = None
        self.next_sibling = None

    def append(self, other):
        if self.current is self:
            other.root = self
            other.parent = self
            if self.children:
                last = self.children[-1]
                last.next_sibling = other
                other.prev_sibling = last
            self.children.append(other)
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

class PyhaaElementOpenable(PyhaaElement):
    def __init__(self, ws_in_left = True, ws_in_right = True, **kwargs):
        self.children = list()
        self.ws_in_left = ws_in_left
        self.ws_in_right = ws_in_right
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
    def __init__(self, name = None, id_ = None, classes = None, static_arguments = None, python_arguments = None, **kwargs):
        self.name = name
        self.id_ = None
        self.classes = set(classes) if classes else set()
        self.static_arguments = dict(static_arguments) if static_arguments else dict()
        self.python_arguments = python_arguments
        super().__init__(**kwargs)
    
class Text(PyhaaElement):
    def __init__(self, text = None, escape = True, **kwargs):
        self.text = text
        self.escape = escape
        super().__init__(**kwargs)

