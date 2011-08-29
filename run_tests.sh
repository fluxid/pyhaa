#!/bin/sh

WORKING_DIR="$(cd "${0%/*}" 2>/dev/null; dirname "$PWD"/"${0##*/}")"
cd ${WORKING_DIR}

nosetests --with-coverage --cover-package=pyhaa --doctest-tests --with-doctest $@ 
