Pyhaa
=====

*Pyhaa* is a templating system, inspired by [HAML](http://haml-lang.com/). It's not meant to be compatible,
and it's not a "port". Only basic rules apply, the rest may be incompatible.

Name is subject to change.

It's a project developed in my free time for my own enjoment,
with little hope someday it gets finished or reach minimal level
of usability.

Not much is done, what is working can be seen in unit tests.

Goals
-----

1. HTML and etree output (for easy generation of XML)
1. Templating basics: inheritance, partials

Decisions
---------

1. Python 3 all the way
1. Forget about pretty-formatting, don't throw whitespaces into HTML if user
   does not ask for it (Instead of "Whitespace Removal" syntax known from HAML
   which doesn't actually solve all problems). Currently easiest option to view
   HTML code are developer tools, available for all modern web browsers, so you don't
   have to worry about pretty HTML.
1. Do not translate template into other templating language. This doubles
   problems and possible bugs you could get with just one and opens door
   to even more horrible, ugly and unmaintainable template code.
1. Forget about automatically "injecting" variables from template context into function
   local scope - use context directly.
1. Make it strict - forget about UNDEFINED objects instead raising error about
   undeclared variable, as this causes more problems than solves.
1. Use as much of Python internals as possible: compile templates into actually inheritable classes
1. Yield instead of writing into io objects
1. Encode into given charset BEFORE compiling template to python code

Copyright and licence
---------------------

Copyright © 2011 Tomasz Kowalczyk

I licence this code under GNU Lesser General Public Licence Version 3

