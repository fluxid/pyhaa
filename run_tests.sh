#!/bin/sh

WORKING_DIR="$(cd "${0%/*}" 2>/dev/null; dirname "$PWD"/"${0##*/}")"
cd ${WORKING_DIR}

export PYTHONPATH="${PWD}/src:${PWD}/../fxd__minilexer/src:${PYTHONPATH}"
nosetests --with-coverage3 --pdb-failures --pdb --cover3-package=pyhaa --doctest-tests --with-doctest tests
