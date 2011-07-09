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

from .. import structure

from ..utils.encode import entity_decode

#log = logging.getLogger(__name__)


BODY_STARTING = (
    'escape', # \
    'text', # foo bar
    'html_raw_toggle', # ?
    'constant', # !
    'tag_name_start', # %
    'tag_class_start', # .
    'tag_id_start', # #
    'code_statement_start', # -
    'code_expression_start', # =
)

class PyhaaParser(Parser):
    def __init__(self, lexer = pyhaa_lexer):
        super().__init__(lexer, True)
        self.indent = 0
        self.tab_width = 0
        self.length = 0
        self.structure = structure.PyhaaStructure()

        self.current_opened = 0
        self.opened_stack = list()

        self.last_tas_name = None
        self.creating_tag = False
        # TODO Merge two above variables into below code
        self.continue_temporary = set()
        self.temporary_info = dict()
        self.body_started = False

        self.constants = {
            'sp': ' ',
            'html5': ('<!DOCTYPE html>', False),
        }

    def test_body_start(self):
        '''
        This function gets called when we matched a token which may start
        template body.
        After we start body, we cannot insert head statements
        '''

    # Below functions are used to hold temporary state

    def get_info(self, name, default):
        return self.temporary_info.get(name, default)

    def continue_info(self, name):
        self.continue_temporary.add(name)

    def set_info(self, name, value):
        self.temporary_info[name] = value
        self.continue_info(name)

    @property
    def escape_next(self):
        return self.get_info('escape_next', True)

    # Handling token matches

    def token_match(self, token, match):
        super().token_match(token, match)

        if not self.body_started and self.indent == 0 and token in BODY_STARTING:
            self.body_started = True

        func = getattr(self, 'handle_' + token, None)
        if func:
            func(match)
            # Don't clear temporary data if we don't handle token
            if self.continue_temporary:
                to_delete = set(self.temporary_info.keys()) - self.continue_temporary
                for key in to_delete:
                    del self.temporary_info[key]
                self.continue_temporary.clear()
            else:
                self.temporary_info.clear()

    def on_bad_token(self):
        raise PyhaaSyntaxError(SYNTAX_INFO.SYNTAX_ERROR, self)


    # BASICS
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

        expected_indent = self.get_info('expected_indent', False)
        if eindent == 0:
            self.indent_re()
        elif eindent < 0:
            self.indent_de(-eindent)
        elif eindent == 1:
            expected_indent = False
            self.indent_in()
        else:
            # Wrong! We can indent only one level at a time!
            raise PyhaaSyntaxError(
                SYNTAX_INFO.TOO_DEEP_INDENT,
                self,
                indent = self.indent,
                new_indent = self.indent + eindent,
            )

        if expected_indent:
            raise PyhaaSyntaxError(
                SYNTAX_INFO.EXPECTED_INDENT,
                self,
            )

    def begin_tag(self):
        self.creating_tag = True
        self.structure.tree.append(structure.Tag())
        self.current_opened += 1

    def end_tag(self):
        self.creating_tag = False
        self.last_tas_name = None

    def handle_inline(self, match):
        self.end_tag()

    def handle_line_end(self, match):
        self.continue_info('expected_indent')
        self.end_tag()
    
    # HEAD stuff
    def handle_head_inherit_expression(self, match):
        self.structure.inheritance.append(match)

    # SMALL stuff
    def handle_text(self, match):
        text = match.group('value')
        self.insert_text(text, self.escape_next)

    def insert_text(self, text, escape):
        if escape:
            # We escape text, but decode entities/unsescape first,
            # we will escape it again at codegen level
            text = entity_decode(text)
        if isinstance(self.structure.tree.current, structure.PyhaaParent):
            children = self.structure.tree.current.children
            if children:
                last_one = children[-1]
                if isinstance(last_one, structure.Text) and last_one.escape == escape:
                    last_one.content = last_one.content.rstrip() + ' ' + text.lstrip()
                    return
        self.structure.tree.append(structure.Text(content = text, escape = escape))
        # PyhaaSimpleContent is not openable, but we must "close" it explicitly when
        # reindenting
        self.current_opened += 1

    def handle_html_raw_toggle(self, match):
        self.set_info('escape_next', False)

    def handle_constant(self, match):
        key = match.group('key')
        value = self.constants.get(key)
        escape = True
        if isinstance(value, (tuple, list)):
            value, escape = value
        if value:
            self.insert_text(value, escape)


    # TAG stuff
    def handle_tag_name_start(self, match):
        self.begin_tag()

    def handle_tag_name(self, match):
        self.structure.tree.current.name = entity_decode(match.group(0))

    def handle_tag_class_start(self, match):
        if not self.creating_tag:
            self.begin_tag()

    def handle_tag_class_name(self, match):
        self.structure.tree.current.classes.add(entity_decode(match.group(0)))

    def handle_tag_id_start(self, match):
        if not self.creating_tag:
            self.begin_tag()

    def handle_tag_id_name(self, match):
        if self.structure.tree.current.id_ is not None:
            raise PyhaaSyntaxError(
                SYNTAX_INFO.ID_ALREADY_SET,
                self,
            )
        self.structure.tree.current.id_ = entity_decode(match.group(0))


    # TAG ATTRIBUTES stuff
    def handle_tas_start(self, match):
        # Ensures that the last attribute-set is a dict so we can set attributes later
        self.structure.tree.current.append_attributes(dict())

    def handle_tas_name(self, match):
        name = entity_decode(match.group('value'))
        self.structure.tree.current.attributes_set[-1][name] = True
        self.last_tas_name = name

    def handle_tas_value(self, match):
        self.structure.tree.current.attributes_set[-1][self.last_tas_name] = entity_decode(match.group('value'))
        self.last_tas_name = None

    def handle_tap_content(self, match):
        self.structure.tree.current.append_attributes(match)


    # PYTHON CODE stuff
    def begin_statement(self, match):
        self.set_info('statement', match.group(1))

    def handle_code_statement_expression(self, match):
        self.begin_statement(match)

    def handle_code_statement_expression_content(self, match):
        self.set_info('statement_expression', match)
        self.continue_info('statement')

    def handle_code_statement_for(self, match):
        self.begin_statement(match)

    def handle_code_statement_for_target(self, match):
        self.set_info('statement_target', match)
        self.continue_info('statement')

    def handle_code_statement_for_expression(self, match):
        self.set_info('statement_expression', match)
        self.continue_info('statement')
        self.continue_info('statement_target')

    def handle_code_statement(self, match):
        self.begin_statement(match)

    def handle_code_colon(self, match):
        statement = self.get_info('statement', None)
        assert statement
        if statement in ('if', 'elif', 'while'):
            expression = self.get_info('statement_expression', None)
            assert expression
            complete = '{} {}:'.format(
                statement,
                expression,
            )
        elif statement == 'for':
            target = self.get_info('statement_target', None)
            expression = self.get_info('statement_expression', None)
            assert target
            assert expression
            complete = '{} {} in {}:'.format(
                statement,
                target,
                expression,
            )
        else:
            complete = statement + ':'
        self.structure.tree.append(structure.CompoundStatement(name = statement, content = complete))
        self.set_info('expected_indent', True)
        self.current_opened += 1

    def handle_code_statement_simple(self, match):
        self.structure.tree.append(structure.SimpleStatement(content = match))
        self.current_opened += 1

    def handle_code_expression_start(self, match):
        self.continue_info('escape_next')

    def handle_code_expression(self, match):
        self.structure.tree.append(structure.Expression(content = match, escape = self.escape_next))
        # PyhaaSimpleContent is not openable, but we must to "close" it explicitly when
        # reindenting
        self.current_opened += 1


    # Indenting
    def indent_de(self, times=1):
        '''
        Dedented line - times attribute means how many levels do we dedent
        '''
        to_close = self.current_opened
        for i in range(times):
            to_close += self.opened_stack.pop()
        self.structure.tree.close(to_close)
        self.current_opened = 0
        self.indent -= times

    def indent_in(self):
        '''
        Indented line
        '''
        if not isinstance(self.structure.tree.current, structure.PyhaaParentNode):
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
        self.structure.tree.close(self.current_opened)
        self.current_opened = 0

    def finish(self):
        self.indent_de(self.indent)

