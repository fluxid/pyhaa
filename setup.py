from setuptools import setup, find_packages
import sys

if sys.version_info < (3,):
    print('Sorry, this package is developed for Python 3')
    exit(1)

setup(
    name = 'pyhaa',
    version = '0.0',
    packages = ['pyhaa'],
    author = 'Tomasz Kowalczyk',
    author_email = 'myself@fluxid.pl',
    description = 'Standalone templating system based on ideas taken from HAML and Mako',
    keywords = 'haml templating',
)

