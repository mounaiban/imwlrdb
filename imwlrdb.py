"""
iMWLRDB: Internet Multi-line Width-Limited Record Database Format

The iMWLRDB (or MWLR for short) is a text database format modeled
after the data formats used by iCalendar, Email, vCard and Usenet.
MWLR attempts to be a generalisation of these formats.

This module contains several functions to map a Python dict to onto
an MWLR database file. Currently, only data export functions are
available; database readers to map, or at least deserialise these
files back into dicts will be added at a later date...

For more information on the format specifications, please check
https://github.com/mounaiban/iMWLRDB/SPECS.rst.

"""
#
# Copyright 2023 Moses Chong
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from itertools import chain, count, islice, repeat, zip_longest
from secrets import token_hex

BEGIN_MARK = 'BEGIN'
EOL_DEFAULT = '\r\n' # End of Line
END_MARK = 'END'
ENCODING_DEFAULT = 'utf8'
FSEP_DEFAULT = ':' # Field Separator
FMSEP_DEFAULT = ';' # Field Separator (multi-value fields)
VSEP_DEFAULT = '=' # Field Separator (sub-fields in multi-value fields)
SFSEP_DEFAULT = ';' # Sub-field Separator
CONFIG_KEY_PREFIX = '__'
UID_KEY = 'UID'
###
FORMAT_DEFAULT = {
    'fsep': FSEP_DEFAULT,
    'fmsep': FMSEP_DEFAULT,
    'eol': EOL_DEFAULT,
    'newline': r'\n',
    'sfsep': SFSEP_DEFAULT,
    'sol': '\x20\x20',  # start of line
    'vsep': VSEP_DEFAULT,
    'width_bytes': 80,
}
FOOTER_KEY = ''.join((CONFIG_KEY_PREFIX, 'footer'))
HEADER_KEY = ''.join((CONFIG_KEY_PREFIX, 'header'))
TYPE_KEY = ''.join((CONFIG_KEY_PREFIX, 'type'))
WORDS_RESERVED = (
    '', BEGIN_MARK, END_MARK, FOOTER_KEY, HEADER_KEY, TYPE_KEY, UID_KEY
)

def multi_val_str(
        d,
        sep_f=VSEP_DEFAULT,
        sep_r=FMSEP_DEFAULT,
        encoding=ENCODING_DEFAULT
    ):
    """
    Return a string containing keys and values of a dict,
    in serialised form.

    By default, the dict {'alfa': 1, 'bravo': 20} becomes
    "alfa=1;bravo=20"

    Currently, only numeric and string keys and values are
    properly supported; dicts work somewhat acceptably.

    Arguments
    ---------
    * sep_f: field-value separator

    * sep_r: dict item separator

    """
    # TODO: Handle nested dicts
    keys = d.keys()
    vals = d.values()
    pairs = zip((f'{k}{sep_f}' for k in keys), (f'{v}{sep_r}' for v in vals))
    return ''.join(chain.from_iterable(pairs))[:-len(sep_r)]

def split_by_max_length(s, L, Lsol=0):
    """
    Break up string 's' into chunks of up to length L.
    Lines after the first will be shortened by Lsol.
    Length includes both Start-of-line and end-of-line symbols

    Function works on both bytes and str. However, the definition
    of length differs; bytes for bytes, characters for str.

    """
    lens = len(s)
    starts = chain((0,), range(L, lens, L-Lsol))
    stops = chain((L,), range(L+(L-Lsol), lens, L-Lsol))
    slices = zip_longest(starts, stops, fillvalue=lens)
    return (s[x:y] for x,y in slices)

def bytes_with_breaks_iter(s, L, eol, sol, encoding):
    """
    Iterator yielding, byte-by-byte, a string 's' where sequence
    'eol' occurs at least once every 'L' bytes.

    For each 'eol' inserted into the string, follow up with start
    of line sequence 'sol' once immediately after.

    The line byte count includes 'sol'.

    """
    byeol = bytes(eol, encoding=encoding)
    bysol = bytes(sol, encoding=encoding)
    #len_bysol = len(bysol)
    bstrs = iter(bytes(s, encoding=encoding).split(byeol))
    for bst in bstrs:
        lenbst = len(bst)
        if lenbst <= L-len(byeol):
            if bst.endswith(byeol):
                yield b''.join((bst,))
                continue
            else:
                yield b''.join((bst, byeol))
                continue
        for x in split_by_max_length(bst, L-len(eol), len(bysol)):
            # TODO: Yield, not return....
            yield b''.join((x, byeol, bysol))

def bytes_with_breaks(s, L, eol, sol, encoding=ENCODING_DEFAULT):
    """
    Return a bytes version of a string 's' as a bytearray with
    line break 'eol' followed by a line start 'sol' every 'L' bytes

    The line byte count includes the line start sequence 'sol'.

    """
    if len(s) <= 0: return b''
    out = b''.join(bytes_with_breaks_iter(s, L, eol, sol, encoding=encoding))
        # TODO: b''.join doesn't work here...
    return out.rstrip(bytes(sol, encoding=encoding))

def imlwldb_iter(
        d,
        uid=None,
        encoding=ENCODING_DEFAULT,
        out_format=FORMAT_DEFAULT,
        need_type=False
    ):
    """
    Iterator yielding bytes of an MLWL database file representation of
    dict 'd'.

    Arguments
    ---------
    * d: dict

    * uid: the UID of database file

    * encoding: encoding of the database file when read as text

    * out_format: dict containing format specification of the
       database file

    * need_type: determines if the __type field is mandatory;
       intended for use only during recursion when serialising
       nested dicts.

    """
    # TODO: Document specs for out_format
    # TODO: Move function calls from iter inner loop to outer loop
    eol = out_format.get('eol', FORMAT_DEFAULT['eol'])
    sol = out_format.get('sol', FORMAT_DEFAULT['sol'])
    fsep = out_format.get('fsep', FORMAT_DEFAULT['fsep'])
    fmsep = out_format.get('fmsep', FORMAT_DEFAULT['fmsep'])
    width = out_format.get('width_bytes', FORMAT_DEFAULT['width_bytes'])

    def mktdict(fd):
        if 'newline' in fd:
            return str.maketrans({'\n': out_format['newline']})
        else: return {}

    tdict = mktdict(out_format)
    keys = (
        key for key in d.keys()
        if (type(key) is str)
        and key.upper() not in WORDS_RESERVED
    )
    footer = d.get(FOOTER_KEY)
    header = d.get(HEADER_KEY) # TODO: test
    if (footer and not header) or (not footer and header):
        raise ValueError('both header and footer must be absent or present')
    rtype = d.get(TYPE_KEY)
    if need_type and not rtype:
        raise ValueError('sub-records must have a type')
    # Record start
    if header:
        yield bytes_with_breaks(header, width, eol, sol, encoding)
    elif rtype and not (header or footer):
        yield bytes_with_breaks(
            ''.join((BEGIN_MARK, fsep, rtype,)),
            width, eol, sol, encoding=encoding
        )
    if uid:
        yield bytes_with_breaks(''.join((UID_KEY, fsep, uid)),
        width, eol, sol, encoding=encoding
    )
    # Fields
    for k in keys:
        if k in WORDS_RESERVED: continue
        obj = d.get(k)
        if type(obj) is dict:
            if '__type' in obj:
                # sub record with BEGIN, END and discrete fields
                for x in imlwldb_iter(d[k], uid=k, need_type=True): yield x
            else:
                # multi-part record:
                # just multiple values crammed into a single field
                mval = multi_val_str(obj)
                yield bytes_with_breaks(
                    ''.join((k, fmsep, mval)),
                    width, eol, sol, encoding=encoding
                )
        else:
            # normal values
            lin: str
            if not k: lin = str(obj).translate(tdict)
            else: lin = ''.join((k, fsep, str(obj).translate(tdict)))
            yield bytes_with_breaks(lin, width, eol, sol, encoding=encoding)

    # Freeform body area
    if '' in d:
        yield bytes_with_breaks(
            str(d.get('')), width, eol, '', encoding=encoding
        )

    # Record end
    if footer:
        yield bytes_with_breaks(footer, width, eol, sol, encoding)
    elif rtype and not (header or footer):
        yield bytes_with_breaks(
            ''.join((END_MARK, fsep, rtype)),
            width, eol, sol, encoding=encoding
        )

def imwlrdb(d, uid=None, encoding=ENCODING_DEFAULT, out_format=FORMAT_DEFAULT):
    """
    Convert a dict 'd' to a MLWL database file. Returns a byte string.

    Arguments
    ---------
    * d: dict

    * uid: the UID of database file

    * encoding: encoding of the database file when read as text

    * out_format: dict containing format specification of the
       database file

    """
    leneol = len((bytes(out_format.get('eol', EOL_DEFAULT), encoding=encoding)))
    return b''.join(imlwldb_iter(d, uid, encoding, out_format))[:-leneol]
