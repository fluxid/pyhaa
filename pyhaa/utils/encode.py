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

import re

from . import dict_sub

# TODO List all entities here
ENTITIES_DECODE = {
    'Aacute': '\u00c1',
    'aacute': '\u00e1',
    'Acirc': '\u00c2',
    'acirc': '\u00e2',
    'acute': '\u00b4',
    'AElig': '\u00c6',
    'aelig': '\u00e6',
    'Agrave': '\u00c0',
    'agrave': '\u00e0',
    'alefsym': '\u2135',
    'Alpha': '\u0391',
    'alpha': '\u03b1',
    'amp': '\u0026',
    'and': '\u2227',
    'ang': '\u2220',
    'apos': '\u0027',
    'Aring': '\u00c5',
    'aring': '\u00e5',
    'asymp': '\u2248',
    'Atilde': '\u00c3',
    'atilde': '\u00e3',
    'Auml': '\u00c4',
    'auml': '\u00e4',
    'bdquo': '\u201e',
    'Beta': '\u0392',
    'beta': '\u03b2',
    'brvbar': '\u00a6',
    'bull': '\u2022',
    'cap': '\u2229',
    'Ccedil': '\u00c7',
    'ccedil': '\u00e7',
    'cedil': '\u00b8',
    'cent': '\u00a2',
    'Chi': '\u03a7',
    'chi': '\u03c7',
    'circ': '\u02c6',
    'clubs': '\u2663',
    'cong': '\u2245',
    'copy': '\u00a9',
    'crarr': '\u21b5',
    'cup': '\u222a',
    'curren': '\u00a4',
    'dagger': '\u2020',
    'Dagger': '\u2021',
    'darr': '\u2193',
    'dArr': '\u21d3',
    'deg': '\u00b0',
    'Delta': '\u0394',
    'delta': '\u03b4',
    'diams': '\u2666',
    'divide': '\u00f7',
    'Eacute': '\u00c9',
    'eacute': '\u00e9',
    'Ecirc': '\u00ca',
    'ecirc': '\u00ea',
    'Egrave': '\u00c8',
    'egrave': '\u00e8',
    'empty': '\u2205',
    'emsp': '\u2003',
    'ensp': '\u2002',
    'Epsilon': '\u0395',
    'epsilon': '\u03b5',
    'equiv': '\u2261',
    'Eta': '\u0397',
    'eta': '\u03b7',
    'ETH': '\u00d0',
    'eth': '\u00f0',
    'Euml': '\u00cb',
    'euml': '\u00eb',
    'euro': '\u20ac',
    'exist': '\u2203',
    'fnof': '\u0192',
    'forall': '\u2200',
    'frac12': '\u00bd',
    'frac14': '\u00bc',
    'frac34': '\u00be',
    'frasl': '\u2044',
    'Gamma': '\u0393',
    'gamma': '\u03b3',
    'ge': '\u2265',
    'gt': '\u003e',
    'harr': '\u2194',
    'hArr': '\u21d4',
    'hearts': '\u2665',
    'hellip': '\u2026',
    'Iacute': '\u00cd',
    'iacute': '\u00ed',
    'Icirc': '\u00ce',
    'icirc': '\u00ee',
    'iexcl': '\u00a1',
    'Igrave': '\u00cc',
    'igrave': '\u00ec',
    'image': '\u2111',
    'infin': '\u221e',
    'int': '\u222b',
    'Iota': '\u0399',
    'iota': '\u03b9',
    'iquest': '\u00bf',
    'isin': '\u2208',
    'Iuml': '\u00cf',
    'iuml': '\u00ef',
    'Kappa': '\u039a',
    'kappa': '\u03ba',
    'Lambda': '\u039b',
    'lambda': '\u03bb',
    'lang': '\u2329',
    'laquo': '\u00ab',
    'larr': '\u2190',
    'lArr': '\u21d0',
    'lceil': '\u2308',
    'ldquo': '\u201c',
    'le': '\u2264',
    'lfloor': '\u230a',
    'lowast': '\u2217',
    'loz': '\u25ca',
    'lrm': '\u200e',
    'lsaquo': '\u2039',
    'lsquo': '\u2018',
    'lt': '\u003c',
    'macr': '\u00af',
    'mdash': '\u2014',
    'micro': '\u00b5',
    'middot': '\u00b7',
    'minus': '\u2212',
    'Mu': '\u039c',
    'mu': '\u03bc',
    'nabla': '\u2207',
    'nbsp': '\u00a0',
    'ndash': '\u2013',
    'ne': '\u2260',
    'ni': '\u220b',
    'not': '\u00ac',
    'notin': '\u2209',
    'nsub': '\u2284',
    'Ntilde': '\u00d1',
    'ntilde': '\u00f1',
    'Nu': '\u039d',
    'nu': '\u03bd',
    'Oacute': '\u00d3',
    'oacute': '\u00f3',
    'Ocirc': '\u00d4',
    'ocirc': '\u00f4',
    'OElig': '\u0152',
    'oelig': '\u0153',
    'Ograve': '\u00d2',
    'ograve': '\u00f2',
    'oline': '\u203e',
    'Omega': '\u03a9',
    'omega': '\u03c9',
    'Omicron': '\u039f',
    'omicron': '\u03bf',
    'oplus': '\u2295',
    'or': '\u2228',
    'ordf': '\u00aa',
    'ordm': '\u00ba',
    'Oslash': '\u00d8',
    'oslash': '\u00f8',
    'Otilde': '\u00d5',
    'otilde': '\u00f5',
    'otimes': '\u2297',
    'Ouml': '\u00d6',
    'ouml': '\u00f6',
    'para': '\u00b6',
    'part': '\u2202',
    'permil': '\u2030',
    'perp': '\u22a5',
    'Phi': '\u03a6',
    'phi': '\u03c6',
    'Pi': '\u03a0',
    'pi': '\u03c0',
    'piv': '\u03d6',
    'plusmn': '\u00b1',
    'pound': '\u00a3',
    'prime': '\u2032',
    'Prime': '\u2033',
    'prod': '\u220f',
    'prop': '\u221d',
    'Psi': '\u03a8',
    'psi': '\u03c8',
    'quot': '\u0022',
    'radic': '\u221a',
    'rang': '\u232a',
    'raquo': '\u00bb',
    'rarr': '\u2192',
    'rArr': '\u21d2',
    'rceil': '\u2309',
    'rdquo': '\u201d',
    'real': '\u211c',
    'reg': '\u00ae',
    'rfloor': '\u230b',
    'Rho': '\u03a1',
    'rho': '\u03c1',
    'rlm': '\u200f',
    'rsaquo': '\u203a',
    'rsquo': '\u2019',
    'sbquo': '\u201a',
    'Scaron': '\u0160',
    'scaron': '\u0161',
    'sdot': '\u22c5',
    'sect': '\u00a7',
    'shy': '\u00ad',
    'Sigma': '\u03a3',
    'sigma': '\u03c3',
    'sigmaf': '\u03c2',
    'sim': '\u223c',
    'spades': '\u2660',
    'sub': '\u2282',
    'sube': '\u2286',
    'sum': '\u2211',
    'sup': '\u2283',
    'sup1': '\u00b9',
    'sup2': '\u00b2',
    'sup3': '\u00b3',
    'supe': '\u2287',
    'szlig': '\u00df',
    'Tau': '\u03a4',
    'tau': '\u03c4',
    'there4': '\u2234',
    'Theta': '\u0398',
    'theta': '\u03b8',
    'thetasym': '\u03d1',
    'thinsp': '\u2009',
    'THORN': '\u00de',
    'thorn': '\u00fe',
    'tilde': '\u02dc',
    'times': '\u00d7',
    'trade': '\u2122',
    'Uacute': '\u00da',
    'uacute': '\u00fa',
    'uarr': '\u2191',
    'uArr': '\u21d1',
    'Ucirc': '\u00db',
    'ucirc': '\u00fb',
    'Ugrave': '\u00d9',
    'ugrave': '\u00f9',
    'uml': '\u00a8',
    'upsih': '\u03d2',
    'Upsilon': '\u03a5',
    'upsilon': '\u03c5',
    'Uuml': '\u00dc',
    'uuml': '\u00fc',
    'weierp': '\u2118',
    'Xi': '\u039e',
    'xi': '\u03be',
    'Yacute': '\u00dd',
    'yacute': '\u00fd',
    'yen': '\u00a5',
    'yuml': '\u00ff',
    'Yuml': '\u0178',
    'Zeta': '\u0396',
    'zeta': '\u03b6',
    'zwj': '\u200d',
    'zwnj': '\u200c',
}
RE_ENTITIES_DECODE = re.compile((
    '&(?:'
    '(?P<char>[a-z0-9]+)|'
    '#(?P<decimal>\d+)|'
    '#x(?P<hexa>[\da-f]+)'
    ');'
), re.I)

# TODO Add white characters to this list
_ENCODEABLE = '&\'"<>'
_ENTITIES_ENCODE = {
    value: key
    for key, value in ENTITIES_DECODE.items()
}
ENTITIES_ENCODE = {
    character: (
        '&#{};'.format(ord(character))
        if entity is None else
        '&{};'.format(entity)
    )
    for character, entity in (
        (character, _ENTITIES_ENCODE.get(character))
        for character in _ENCODEABLE
    )
}
del _ENTITIES_ENCODE, _ENCODEABLE

entity_encode = dict_sub(ENTITIES_ENCODE)

def _entity_decode(match):
    whole = match.group(0)
    char = match.group('char')
    if char:
        return ENTITIES_DECODE.get(char, whole)
    decimal = match.group('decimal')
    if decimal:
        return chr(int(decimal))
    hexa = match.group('hexa')
    if hexa:
        return chr(int(hexa, 16))
    return whole # pragma: no cover

def entity_decode(value):
    return RE_ENTITIES_DECODE.sub(_entity_decode, value)

def single_encode(value, do_byte_encode = True, do_entity_encode = False, encoding = 'utf-8'):
    if isinstance(value, str):
        if do_entity_encode:
            value = entity_encode(value)
        if do_byte_encode:
            value = value.encode(encoding, encoding)
    return value

def recursive_encode(value, do_byte_encode = True, do_entity_encode = False, encoding = 'utf-8'):
    # Of course, it doesn't cover all possibilities
    if isinstance(value, bytes) or not (do_byte_encode or do_entity_encode):
        return value

    if isinstance(value, dict):
        return {
            single_encode(key): recursive_encode(value, do_byte_encode, do_entity_encode, encoding)
            for key, value in value.items()
        }

    type_ = None
    if isinstance(value, set):
        type_ = set
    elif isinstance(value, (list, tuple)):
        type_ = list

    if not type_:
        return single_encode(value, do_byte_encode, do_entity_encode, encoding)
    
    return type_((
        recursive_encode(item, do_byte_encode, do_entity_encode, encoding)
        for item in value
    ))

