"""
iMWLRDB: Internet Multi-line Width-Limited Record Database Format

Main module unit tests

"""
#
# Copyright 2023 Moses Chong
#
# Licensed under the terms and conditions of the
# Apache License Version 2.0.
#
from unittest import TestCase
from imwlrdb import imwlrdb, bytes_with_breaks, EOL_DEFAULT

# NOTE: Long reference strings are split into multiple strings to
# avoid excess whitespace in the strings

EOL = bytes(EOL_DEFAULT, encoding='utf8')

class bytesWithBreaksTests(TestCase):
    # NOTE: these functions return line-terminating characters.
    # Line-terminating chars output by bytes_with_breaks() will be
    # stripped in the final text file.
    #
    # PROTIP: width limit 'L' includes start-of-line
    #  and end-of-line symbols

    def test_empty(self):
        args = {
            's': '',
            'L': 16,
            'eol': '\r\n',
            'sol': '\x20\x20'
        }
        self.assertEqual(bytes_with_breaks(**args), b'')

    def test_break_length(self):
        args = {
            's': 'abcdefgh123456',
            'L': 16,
            'eol': '\r\n',
            'sol': '\x20\x20'
        }
        ref = b'abcdefgh123456\r\n'
        self.assertEqual(bytes_with_breaks(**args), ref)

    def test_break_length_with_br_end(self):
        args = {
            's': 'abcdefgh123456\r\n',
            'L': 16,
            'eol': '\r\n',
            'sol': '\x20\x20'
        } # TODO: does this contradict EOL footer tests below?
        ref = b'abcdefgh123456\r\n'
        self.assertEqual(bytes_with_breaks(**args), ref)

    def test_longer_than_break_length_1_over(self):
        args = {
            's': 'abcdefgh12345678A',
            'L': 16,
            'eol': '\r\n',
            'sol': '\x20\x20'
        }
        ref = b''.join((
            b'abcdefgh123456\r\n',
            b'\x20\x2078A\r\n'
        ))
        self.assertEqual(bytes_with_breaks(**args), ref)

    def test_longer_than_break_length_1_5(self):
        args = {
            's': 'abcdefgh12345678ABCDEF',
            'L': 16,
            'eol': '\r\n',
            'sol': '\x20\x20'
        }
        ref = b''.join((
            b'abcdefgh123456\r\n',
            b'\x20\x2078ABCDEF\r\n'
        ))
        self.assertEqual(bytes_with_breaks(**args), ref)

    def test_longer_than_break_length_2_almost(self):
        args = {
            's': 'abcdefgh12345678ABCDEFGH123456',
            'L': 16,
            'eol': '\r\n',
            'sol': '\x20\x20'
        }
        ref = b''.join((
            b'abcdefgh123456\r\n',
            b'\x20\x2078ABCDEFGH12\r\n'
            b'\x20\x203456\r\n'
        ))
        self.assertEqual(bytes_with_breaks(**args), ref)

    def test_longer_than_break_length_2(self):
        args = {
            's': 'abcdefgh12345678ABCDEFGH12345678',
            'L': 16,
            'eol': '\r\n',
            'sol': '\x20\x20'
        }
        ref = b''.join((
            b'abcdefgh123456\r\n',
            b'\x20\x2078ABCDEFGH12\r\n'
            b'\x20\x20345678\r\n'
        ))
        self.assertEqual(bytes_with_breaks(**args), ref)

    def test_shorter_than_break_length(self):
        args = {
            's': 'abcdefgh12345',
            'L': 16,
            'eol': '\r\n',
            'sol': '\x20\x20'
        }
        ref = b'abcdefgh12345\r\n'
        self.assertEqual(bytes_with_breaks(**args), ref)

    def test_shorter_than_break_length_with_br(self):
        args = {
            's': 'abcdefgh\r\n123456',
            'L': 16,
            'eol': '\r\n',
            'sol': '\x20\x20'
        }
        ref = b'abcdefgh\r\n123456\r\n'
        self.assertEqual(bytes_with_breaks(**args), ref)

class imwlrdbTests(TestCase):

    def test_empty(self):
        d = {}
        self.assertEqual(imwlrdb(d), b'')

    def test_footer_eq_eol(self):
        """When footer == eol, the original EOL must remain"""
        d = {
            '__header': '*****',
            '__footer': EOL_DEFAULT, # PROTIP: EOL_DEFAULT is the original str
            'ALFA': 0,
            'BRAVO': 'excel',
        }
        ref = b''.join((
            b'*****', EOL,
            b'ALFA:0', EOL,
            b'BRAVO:excel', EOL,
            EOL
        ))
        self.assertEqual(imwlrdb(d), ref)

    def test_footer_without_header(self):
        d = {
            '__footer': '-----',
            'ALFA': 0,
            'BRAVO': 'excel',
        }
        with self.assertRaises(ValueError):
            imwlrdb(d)

    # TODO: more custom format tests
    def test_format_custom_fsep(self):
        fmt = {
            'fsep': ':\x20',
        }
        d = {
            '__header': 'FROM MAILER DAEMON WITH LOVE',
            '__footer': '\r\n',
            'From': 'amor@example.com',
            'To': 'baci@example.com'
        }
        args = {
            'out_format': fmt,
        }
        ref = b''.join((
            b'FROM MAILER DAEMON WITH LOVE', EOL,
            b'From: amor@example.com', EOL,
            b'To: baci@example.com', EOL,
            EOL
        ))
        self.assertEqual(imwlrdb(d, **args), ref)

    def test_header_footer(self):
        d = {
            '__header': '-----',
            '__footer': '-----',
            'ALFA': 0,
            'BRAVO': 'excel',
        }
        ref = b''.join((
            b'-----', EOL,
            b'ALFA:0', EOL,
            b'BRAVO:excel', EOL,
            b'-----'
        ))
        self.assertEqual(imwlrdb(d), ref)

    def test_header_footer_vs_type(self):
        """__footer suppresses __type"""
        d = {
            '__footer': '-----',
            '__type': 'RECORD',
            '__header': '-----',
            'ALFA': 0,
            'BRAVO': 'excel',
        }
        ref = b''.join((
            b'-----', EOL,
            b'ALFA:0', EOL,
            b'BRAVO:excel', EOL,
            b'-----'
        ))
        self.assertEqual(imwlrdb(d), ref)

    def test_header_without_footer(self):
        d = {
            '__header': '-----',
            'ALFA': 0,
            'BRAVO': 'excel',
        }
        with self.assertRaises(ValueError):
            imwlrdb(d)

    def test_one_level(self):
        d = {
            '__type': 'RECORD',
            'ALFA': 0,
            'BRAVO': 'excel'
        }
        ref = b''.join((
            b'BEGIN:RECORD', EOL,
            b'ALFA:0', EOL,
            b'BRAVO:excel', EOL,
            b'END:RECORD',
        ))
        self.assertEqual(imwlrdb(d), ref)

    def test_one_level_with_freeform_body(self):
        d1 = {
            'ALFA': 0,
            'BRAVO': 'excel',
            '': 'Nobody here'
        }
        ref = b''.join((
            b'ALFA:0', EOL,
            b'BRAVO:excel', EOL,
            b'Nobody here'
        ))
        self.assertEqual(imwlrdb(d1), ref)

    def test_one_level_with_freeform_body_header_and_footer(self):
        """
        The freeform body area always appears second last,
        and the footer is always last
        """
        d1 = {
            '__footer': EOL_DEFAULT,
            'ALFA': 0,
            '__header': '-----',
            '': 'Nobody here',
            'BRAVO': 'excel'
        }
        ref = b''.join((
            b'-----', EOL,
            b'ALFA:0', EOL,
            b'BRAVO:excel', EOL,
            b'Nobody here', EOL,
            EOL
        )) # TODO: find out how to deal with double footer
        self.assertEqual(imwlrdb(d1), ref)

    def test_one_level_with_freeform_body_not_last(self):
        """The freeform body area always appears second last"""
        d1 = {
            '': 'Nobody here',
            'ALFA': 0,
            'BRAVO': 'excel'
        }
        ref = b''.join((
            b'ALFA:0', EOL,
            b'BRAVO:excel', EOL,
            b'Nobody here'
        ))
        self.assertEqual(imwlrdb(d1), ref)

    def test_one_level_no_type(self):
        d = {'ALFA': 0, 'BRAVO': 'excel'}
        ref = b''.join((
            b'ALFA:0', EOL,
            b'BRAVO:excel'
        ))
        self.assertEqual(imwlrdb(d), ref)

    def test_reserved_keys_begin_end(self):
        """
        Reserved words BEGIN and END are not allowed
        and are to be ignored.
        """

        d = {'BEGIN': '20670401', 'END': '20670402', 'CHARLIE': 0}
        ref = b'CHARLIE:0'
        self.assertEqual(imwlrdb(d), ref)

    def test_two_level(self):
        d = {
            '__type': 'RECORD',
            'ALFA': 0,
            'BRAVO': 'excel',
            'deadbeefcafe0000f000': {
                '__type': 'SUB_RECORD',
                'CHARLIE': -1,
                'DELTA': 'more'
            }
        }
        ref = b''.join((
            b'BEGIN:RECORD', EOL,
            b'ALFA:0', EOL,
            b'BRAVO:excel', EOL,
            b'BEGIN:SUB_RECORD', EOL,
            b'UID:deadbeefcafe0000f000', EOL,
            b'CHARLIE:-1', EOL,
            b'DELTA:more', EOL,
            b'END:SUB_RECORD', EOL,
            b'END:RECORD'
        ))
        self.assertEqual(imwlrdb(d), ref)

    def test_two_level_uid_priority(self):
        """Ignore the UID property for sub-records, regardless of case"""

        d1 = {
            '__type': 'RECORD',
            'ALFA': 0,
            'BRAVO': 'excel',
            'deadbeefcafe0000f000': {
                '__type': 'SUB_RECORD',
                'UID': 420690,
                'CHARLIE': -1,
                'DELTA': 'more'
            }
        }

        d2 = {
            '__type': 'RECORD',
            'ALFA': 0,
            'BRAVO': 'excel',
            'deadbeefcafe0000f000': {
                '__type': 'SUB_RECORD',
                'UId': 420690,
                'CHARLIE': -1,
                'DELTA': 'more'
            }
        }

        d6 = {
            '__type': 'RECORD',
            'ALFA': 0,
            'BRAVO': 'excel',
            'deadbeefcafe0000f000': {
                '__type': 'SUB_RECORD',
                'uid': 420690,
                'CHARLIE': -1,
                'DELTA': 'more'
            }
        }

        ref = b''.join((
            b'BEGIN:RECORD', EOL,
            b'ALFA:0', EOL,
            b'BRAVO:excel', EOL,
            b'BEGIN:SUB_RECORD', EOL,
            b'UID:deadbeefcafe0000f000', EOL,
            b'CHARLIE:-1', EOL,
            b'DELTA:more', EOL,
            b'END:SUB_RECORD', EOL,
            b'END:RECORD'
        ))
        for x in (d1, d2, d6):
            self.assertEqual(imwlrdb(x), ref)

    def test_two_level_2L_no_type(self):
        """Without a type, nested records will map into multi-value field"""
        d = {
            '__type': 'RECORD',
            'ALFA': 0,
            'BRAVO': 'excel',
            'CHARLIE': {
                'DELTA': -1,
                'ECHO': 'hi'
            }
        }
        ref = b''.join((
            b'BEGIN:RECORD', EOL,
            b'ALFA:0', EOL,
            b'BRAVO:excel', EOL,
            b'CHARLIE;DELTA=-1;ECHO=hi', EOL,
            b'END:RECORD'
        ))
        self.assertEqual(imwlrdb(d), ref)
