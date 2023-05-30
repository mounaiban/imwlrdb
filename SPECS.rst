==================================
iMWLRDB Preliminary Specifications
==================================

Internet Multi-line Width-Limited Record Database File Specs
Version 1.2

Copyright 2023 Moses Chong

This specification is brought to you under the terms and conditions of
the Creative Commons Attribution-ShareAlike 4.0 International license.

For full terms and conditions, visit: https://creativecommons.org/licenses/by-sa/4.0/

Some parts of the Specification may be altered to suit a user's needs;
the list of available customisations may be found in the section *User
Configurable Specifications* below.

---------
Structure
---------

An MWLR file is a text file, limited to a predefined number of bytes
per line. A line is defined th between end-of-line symbols (EOLs).
The width limit includes end-of-line and start-of-line symbols (SOLs).

Each byte has eight bits and the default encoding is UTF-8.

The file contains one or more data items, or records.

Records
=======

Each record is a data item containing one or more sub-items or fields.
In a file with multiple records, the requirement to have the same
exact fields for every record, or to be *structured* is left to the
user's application.

Fields
------

Fields may take one or more lines, and may have one or more values.
If a field takes up more than one line, each overflowing line begins
with an SOL. A field begins with the field name, followed by a
separator (``FSEP``) and then one or more values.

Multi-value fields may be encoded as a single multi-value field, or as
a sub-record.

Reserved Field Names
--------------------

The following field names cannot be used, as they are reserved for
use by database structures. The list is case-insensitive.

* ``__footer``

* ``__header``

* ``__type``

* ``BEGIN``

* ``END``

* ``UID``

Multi-Value Fields
------------------

Fields with multiple values are inidcated by a multi-value field
separator, ``FMSEP``.

When there are multiple values in a field, values must be separated
with a value separator (``VSEP``).

Each value may have a name, making such values sub-fields; names must
only be used once per field, and is separated from the value by a
sub-field separator (``SFSEP``).

Named and unnamed values cannot be used together in the same field.
There is no defined method of handling separator collisions; this is
left to the user to decide.

MWLR Value Types
----------------

All MWLR values are strings; it is up to the user's application to
determine what type to convert each field to when the database file is
read back.

  TODO: suggest ways to encapsulate type conversion information into
  an MWLR file

Record Start and End
====================

In a file with multiple records, the each record must have a clearly-
defined start and end.

Record Type
-----------

By default, the record begins with a special marker which looks like a
field with the name ``BEGIN``, and with a value of the record's type.

Likewise, the record end would do the same with the word ``END``, with
a field separator followed by the same type used in the corresponding
``BEGIN``.

Please note that the record markers are not actually fields, despite
their appearance.

Arbitrary Header and Footer
---------------------------

User-defined record starts and ends are supported, and may be set for
each individual record. Both the header and footer must be present or
absent at the same time; one cannot be used without the other.

Setting the header and footer will suppress the default record start
and end markers.

To ensure that the record is legible to readers, please ensure that
headers and footers are easy to tell apart from record fields.

Freeform Content Area
=====================

*New in v1.1*

A record may contain a single freeform content area as its last field.
This freeform area does not have any SOLs nor field names, and is
terminated by a single empty line.

Examples
========

  TODO

===========================
User-defined Specifications
===========================

The following parts of the specifications can be set by the user:

* ``__header`` (no default)

* ``__footer`` (no default)

* ``SOL`` (default: two spaces; Python: ``'\x20\x20'``)

* ``EOL`` (default: CRLF; C, Python et. al.: ``'\r\n'``)


New in v1.2:

* ``FSEP`` (default: single colon without spaces; ``':'``;
  Unicode: ``U+003A``)

* ``SFSEP`` (default: equals sign without spaces; ``'='``; ``U+003D``)

* ``VSEP`` (default: semicolon; ``';'``; ``U+003B``)

-------
Mapping
-------

This is a brief description of how ``dicts`` map to MWLR files:

The outermost ``dict`` maps to a single-record file or the
file-level context of the file in multile-record files.

Inner ``dict``'s map to multi-value fields, or records in a
multi-record file.

To form a record, an inner dict must have either a type (key:
``__type``) or a header and footer (keys: ``__header`` and
``__footer``). If there is no type or a header and footer, the record
will instead map into a multi-value field.

The freeform data body area is mapped by an item with the empty string
key (``''``).

Only values with keys of type ``str`` will be mapped, non-``str`` keys
will be ignored.
