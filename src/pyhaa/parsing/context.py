# -*- coding: utf-8 -*-

#import logging

from fxd.minilexer import BasicContext

from .errors import (
    PyhaaSyntaxError,
    SYNTAX_INFO,
    warn_syntax,
)

from ..structure import (
    PyhaaTree,
    PyhaaElementOpenable,
    Tag,
    Text,
)

#log = logging.getLogger(__name__)


class PyhaaParsingContext(BasicContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent = 0
        self.tab_width = 0
        self.length = 0
        self.tree = PyhaaTree()

        self.current_opened = 0
        self.opened_stack = list()

        self.last_tas_name = None
        self.creating_tag = False

    def token_match(self, token, match):
        super().token_match(token, match)
        func = getattr(self, 'handle_' + token, None)
        if func:
            func(match)

    def handle_indent(self, match):
        match = match.group(0)
        tabs = match.count('\t')
        spaces = match.count(' ')

        if tabs and spaces:
            warn_syntax(
                SYNTAX_INFO.INDENT_TAB_SPACES,
                self,
                tabs = tabs,
                spaces = spaces,
            )

        eindent = tabs - self.indent

        if spaces:
            if self.tab_width:
                # We know tab width, use it then
                a, b = divmod(spaces, self.tab_width)
                if b:
                    # Not good - undividable count of spaces
                    raise PyhaaSyntaxError(
                        SYNTAX_INFO.INCONSISTENT_TAB_WIDTH,
                        self,
                        tabs = tabs,
                        spaces = spaces,
                        width = self.tab_width,
                        indent = self.indent,
                    )
                eindent += a
            else:
                # Or not - detect it 
                if eindent == 0:
                    # Count of tabs is equal to current indent.
                    # We have some additional spaces, so it's probalbly
                    # line indented one level, and count of those
                    # spaces is tab width
                    self.tab_width = spaces
                    eindent = 1
                elif eindent < 0:
                    # We have less tabs than current indent levels.
                    # Let's guess tab width from the difference
                    a, b = divmod(spaces, -eindent)
                    if b:
                        # Undividable space count - we can't handle that
                        raise PyhaaSyntaxError(
                            SYNTAX_INFO.INVALID_INDENT,
                            self,
                            tabs = tabs,
                            spaces = spaces,
                            indent = self.indent,
                        )
                    self.tab_width = a
                    eindent = 0
                else:
                    # So we have more tabs than indent level and additional
                    # spaces, and that's incorrect
                    raise PyhaaSyntaxError(
                        SYNTAX_INFO.INVALID_INDENT,
                        self,
                        tabs = tabs,
                        spaces = spaces,
                        indent = self.indent,
                    )

        if eindent == 0:
            self.indent_re()
        elif eindent < 0:
            self.indent_de(-eindent)
        elif eindent == 1:
            self.indent_in()
        else:
            # Wrong! We can indent only one level at a time!
            raise PyhaaSyntaxError(
                SYNTAX_INFO.TOO_DEEP_INDENT,
                self,
                indent = self.indent,
                new_indent = self.indent + eindent,
            )

    def begin_tag(self):
        self.creating_tag = True
        self.tree.append(Tag())
        self.current_opened += 1

    def end_tag(self):
        self.creating_tag = False
        self.last_tas_name = None

    def handle_line_end(self, match):
        self.end_tag()

    def handle_tag_name_start(self, match):
        self.begin_tag()

    def handle_tag_name(self, match):
        self.tree.current.name = match.group(0)

    def handle_tag_class_start(self, match):
        if not self.creating_tag:
            self.begin_tag()

    def handle_tag_class_name(self, match):
        self.tree.current.classes.add(match.group(0))

    def handle_tag_id_start(self, match):
        if not self.creating_tag:
            self.begin_tag()

    def handle_tag_id_name(self, match):
        if self.tree.current.id_ is not None:
            raise PyhaaSyntaxError(
                SYNTAX_INFO.ID_ALREADY_SET,
                self,
            )
        self.tree.current.id_ = match.group(0)

    def handle_continue_inline(self, match):
        self.end_tag()

    def handle_text(self, match):
        lol = Text(match.group(0))
        self.tree.append(lol)
        # Text is not openable, but we must to "close" it explicitly when
        # reindenting
        self.current_opened += 1

    def handle_tas_name(self, match):
        name = match.group('value')
        self.tree.current.simple_attributes[name] = True
        self.last_tas_name = name

    def handle_tas_value(self, match):
        self.tree.current.simple_attributes[self.last_tas_name] = match.group('value')
        self.last_tas_name = None

    def handle_tap_rest(self, match):
        self.tree.current.python_attributes = match

    def indent_de(self, times=1):
        '''
        Dedented line - times attribute means how many levels do we dedent
        '''
        to_close = self.current_opened
        for i in range(times):
            to_close += self.opened_stack.pop()
        self.tree.close(to_close)
        self.current_opened = 0
        self.indent -= times

    def indent_in(self):
        '''
        Indented line
        '''
        if not isinstance(self.tree.current, PyhaaElementOpenable):
            raise PyhaaSyntaxError(
                SYNTAX_INFO.UNEXPECTED_INDENT,
                self,
            )
        self.opened_stack.append(self.current_opened)
        self.current_opened = 0
        self.indent += 1

    def indent_re(self):
        '''
        Continuing at the same indent level
        '''
        self.tree.close(self.current_opened)
        self.current_opened = 0

    def finish(self):
        self.indent_de(self.indent)

