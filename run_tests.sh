#!/bin/sh

WORKING_DIR="$(cd "${0%/*}" 2>/dev/null; dirname "$PWD"/"${0##*/}")"
cd ${WORKING_DIR}

nosetests --with-coverage3 --cover3-package=pyhaa --doctest-tests --with-doctest tests
#nosetests --with-coverage3 -s --pdb --pdb-failures --cover3-package=pyhaa --doctest-tests --with-doctest tests
