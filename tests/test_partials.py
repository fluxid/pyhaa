# -*- coding: utf-8 -*-

'''
Testing partial stuff...
'''

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

from pyhaa import (
    html_render_to_string,
    parse_string,
    PyhaaEnvironment,
    structure,
)
from pyhaa.runtime.loaders import FilesystemLoader

from .helpers import jl, PyhaaTestCase

class TestPartials(PyhaaTestCase):
    def test_basic_partial_one(self):
        struct = parse_string(jl(
            '`def hello(a, b, c):',
            '  %h1 partial',
            '  =a',
            '  =b',
            '  =c',
            '=self.hello("a", "b", "c")',
        ))
        self.assertEqual(len(struct.partials), 1)
        self.assertIn('hello', struct.partials)
        code1, = struct.tree
        self.assert_(isinstance(code1, structure.Expression))
        self.assertEqual(len(struct.partials['hello']), 4)

    def test_basic_partial_two(self):
        struct = parse_string(jl(
            '`def hello(a, b, c):',
            '  %h1 partial',
            '  =a',
            '  =b',
            '  =c',
            '`def lol():',
            '  lol',
            '=self.hello("a", "b", "c")',
            '=self.lol()',
        ))
        self.assertEqual(len(struct.partials), 2)
        self.assertIn('hello', struct.partials)
        self.assertIn('lol', struct.partials)
        code1, code2 = struct.tree
        self.assert_(isinstance(code1, structure.Expression))
        self.assert_(isinstance(code2, structure.Expression))
        self.assertEqual(len(struct.partials['hello']), 4)
        self.assertEqual(len(struct.partials['lol']), 1)

    def test_optional_colon(self):
        # Should pass, we're declaring empty partial
        parse_string(jl(
            '`def prototype()',
            '',
            '%',
        ))

        # Should pass (catch exception) as there is colon
        self.assertPSE(
            'EXPECTED_INDENT',
            parse_string,
            jl(
                '`def incomplete():',
                '',
                '%',
            ),
        )

        # Should pass (catch exception) as there is no colon and we define something inside
        self.assertPSE(
            'UNEXPECTED_INDENT',
            parse_string,
            jl(
                '`def incomplete()',
                '  %',
                '%',
            ),
        )

    def test_runtime(self):
        loader = FilesystemLoader(paths='./tests/files/partials', input_encoding = 'utf-8')
        environment = PyhaaEnvironment(loader = loader)

        def render(path):
            template = environment.get_template(path)
            return html_render_to_string(template)

        self.assertEqual(
            render('base.pha'),
            '<html><head><title>Web page</title></head><body></body></html>',
        )

        self.assertEqual(
            render('page.pha'),
            '<html><head><title>Subpage - Web page</title></head><body><h1>Hello</h1></body></html>',
        )


