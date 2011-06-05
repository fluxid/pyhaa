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
1. Macros and constants for pre-codegen "dynamics"
1. Allow to write clean, but strict template code

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

TODO
----

Things I left behind for later, not those "yet to be touched".

1. Refactor python-code matchers - rethink how to handle tokenizer readahead
1. Better unit-test error handling
1. Reorganize and clean up code in parser, lexer and think of better names for code-related tokens
1. Handle this code correctly: `-while 1: %p -break` or `%p -return`
   (This results in opened, but not closed p tag. `try..finally` ? Dumping all tag-closes just before break/return?)
1. Handle errors raised in exec (while compiling template) more correctly (StopIteration
   raised in the template code may cause strange behavior)
1. Find better way for inserting whitespaces (`!sp` syntax is too a bit ugly)
1. Make setting tag attributes from variable easier (currently only dict-comprehension is possible)

What still needs some thought
-----------------------------

Things I didn't yet start implementing

1. How should inheritance actually work? How about creating dynamically a new type and instantiating it immediately?
1. How should template loading work?
1. What syntax for module/class level code? (How to differentiate code meant to be placed on module or class level?
   When should be default `body` function opened?)

Copyright and licence
---------------------

Copyright © 2011 Tomasz Kowalczyk

I licence this code under GNU Lesser General Public Licence Version 3

