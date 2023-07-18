=======
iMWLRDB
=======

Internet Multi-line Width-Limited Record Database Format

--------
Overview
--------

The iMWLRDB, or the *MWLR* format for short, is an attempt to
generalise the data formats used by iCalendar (RFC 2445 and
successors), Email (RFC 2822 et. al) vCard (RFC 6350) and Usenet
(RFC 850 et. al), into a customsiable and extensible database format.

These databases are text files containing one or more records.
Each record contains fields which begin on a new line. Each line in
the file begins with a field name, followed by a separator symbol
before the field value. Records may be nested, and multiple values may
be crammed into a single field.

The databases do not have to be structured; each record in a database
need not contain the same fields.

Lines have a width limit; there must be at least one line break
every maximum number of bytes, while continuing lines optionally begin
with a start-of-line sequence before the value content.

This mini-project was also an attempt at functional programming in
Python. Functional Python isn't as pretty as Haskell, but it's
pretty usable!

--------
Contents
--------

For now there is only a means of converting ``dict``'s into database
files, some unit tests, and sample databases.

A database deserialiser to read files back into ``dict``'s will be added
at a later date.

---------------------------
Specifications and Examples
---------------------------

For detailed specifications, please refer to ``SPECS.rst`` in the
repository's root directory. A small collection of sample databases
may be found in the ``demo.py`` module.

-------
License
-------

All code is licensed under the terms and conditions of the `Apache License`_,
Version 2.0.

The specifications (``SPECS.rst``) are licensed under the terms and
conditions of the Creative Commons `BY-SA 4.0`_.

.. _Apache License: http://www.apache.org/licenses/LICENSE-2.0

.. _BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/
