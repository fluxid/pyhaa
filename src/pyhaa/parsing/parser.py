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

#import logging

from fxd.minilexer import Parser

from .errors import (
    PyhaaSyntaxError,
    SYNTAX_INFO,
    warn_syntax,
)
from .lexer import pyhaa_lexer

from ..structure import (
    PyhaaParentNode,
    PyhaaParent,
    PyhaaTree,
    Tag,
    Text,
)

from ..utils.encode import entity_decode

#log = logging.getLogger(__name__)


class PyhaaParser(Parser):
    def __init__(self):
        super().__init__(pyhaa_lexer, True)
        self.indent = 0
        self.tab_width = 0
        self.length = 0
        self.tree = PyhaaTree()

        self.current_opened = 0
        self.opened_stack = list()

        self.last_tas_name = None
        self.creating_tag = False
        self.escape_next = True

    def token_match(self, token, match):
        super().token_match(token, match)
        func = getattr(self, 'handle_' + token, None)
        if func:
            func(match)
        if token != 'html_escape_toggle':
            self.escape_next = True

    def on_bad_token(self):
        raise PyhaaSyntaxError(SYNTAX_INFO.SYNTAX_ERROR, self)

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
        text = match.group('value')
        if self.escape_next:
            # We escape text, but decode entities/unsescape first,
            # we will escape it again at codegen level
            text = entity_decode(text)
        if isinstance(self.tree.current, PyhaaParent):
            children = self.tree.current.children
            if children:
                last_one = children[-1]
                if isinstance(last_one, Text) and last_one.escape == self.escape_next:
                    last_one.text = last_one.text + ' ' + text
                    return
        self.tree.append(Text(text, escape = self.escape_next))
        # Text is not openable, but we must to "close" it explicitly when
        # reindenting
        self.current_opened += 1

    def handle_tas_start(self, match):
        # Ensures that the last attribute-set is a dict so we can set attributes later
        self.tree.current.append_attributes(dict())

    def handle_tas_name(self, match):
        name = match.group('value')
        self.tree.current.attributes_set[-1][name] = True
        self.last_tas_name = name

    def handle_tas_value(self, match):
        self.tree.current.attributes_set[-1][self.last_tas_name] = match.group('value')
        self.last_tas_name = None

    def handle_tap_rest(self, match):
        self.tree.current.append_attributes(match)

    def handle_html_escape_toggle(self, match):
        self.escape_next = False

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
        if not isinstance(self.tree.current, PyhaaParentNode):
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

