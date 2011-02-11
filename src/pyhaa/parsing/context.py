# -*- coding: utf-8 -*-

#import logging

from fxd.minilexer import BasicContext

from .errors import (
    PyhaaSyntaxError,
    SYNTAX_INFO,
    warn_syntax,
)

#log = logging.getLogger(__name__)


class PyhaaParsingContext(BasicContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent = 0
        self.tab_width = 0
        self.length = 0
        #self.tree = PyhaaTree()

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
                        raise Exception
                    self.tab_width = a
                    eindent = 0
                else:
                    # So we have more tabs than indent level and additional
                    # spaces, and that's incorrect
                    raise Exception

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

    def indent_de(self, times=1):
        '''
        Dedented line - times attribute means how many levels do we dedent
        '''
        self.indent -= times

    def indent_in(self):
        '''
        Indented line
        '''
        self.indent += 1

    def indent_re(self):
        '''
        Continuing at the same indent level
        '''
        pass

