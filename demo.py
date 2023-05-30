"""
iMWLRDB: Internet Multi-line Width-Limited Record Database Format

Sample Databases

"""
from datetime import datetime
from zoneinfo import ZoneInfo
from os import path
#
from imwlrdb import imwlrdb, bytes_with_breaks, FORMAT_DEFAULT

def mwlr_file(d, fpath, out_format=FORMAT_DEFAULT):
    """Convert dict, str list or tuple to MWLR database and write to file"""
    with open(path.expanduser(fpath), mode='wb') as f:
        if type(d) in (list, tuple):
            for x in d:
                if type(x) is dict:
                    f.write(imwlrdb(x, out_format=out_format))
        elif type(d) is dict: f.write(imwlrdb(d, out_format=out_format))
        elif type(d) is str:
            f.write(bytes_with_breaks(d, 40, '\r\n', '\x20\x20'))
        else: raise TypeError('sorry, object is of an unsupported type')

def date_styles(dt):
    """Return dict of a datetime in different formats"""
    DAEMON_DAYS = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    DAEMON_MONTHS = (
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    )

    dtpart = dt.isoformat().partition('+')
    return {
        'daemon': ''.join((
            "From MAILER DAEMON  ",
            f"{DAEMON_DAYS[dt.weekday()]} ",
            f"{DAEMON_MONTHS[dt.month-1]} ",
            f"{dt.day} {dt.hour:02}:{dt.minute:02}:{dt.second:02} {dt.year}"
        )),
        'Message-ID': f"<{dt.timestamp()}@example.com>",
        'RFC2822-Date': ''.join((
            f"{DAEMON_DAYS[dt.weekday()]}, ",
            f"{dt.day} {dt.month} {dt.year} ",
            f"{dt.hour:02}:{dt.minute:02}:{dt.second:02} ",
            f"{dtpart[1]}{dtpart[2]}"
        ))
    }


# Contact info
# ============
# One-level database
# Tested on Evolution
#
contact = {
    '__type': 'VCARD',
    'VERSION': '4.0',
    'KIND': 'individual',
    'N': 'Hu;David;;',
    'NICKNAME': 'dave11',
    'BDAY': '20051225',
    'CATEGORIES': 'hacker',
    'EMAIL': 'beabrvh@example.com',
    'GENDER': 'M', # He/Him; cis
    'LANG': 'en-AU',
    'NOTE': 'iMWLR test\\nVirtual Contact File',
    'TZ': "Australia/Melbourne",
}


# Email archive (Berkeley Mailbox)
# ================================
# Tested on Evolution
# References: lore.kernel.org, Wikipedia: Mbox
#
# This example contains a list of multiple one-level databases.
# For correct output, please use the 'emails_format' output format
# configuration below.
#
emails = [
    {
        '__header': 'From MAILER DAEMON  Sat Dec 26 10:12:22 2026',
        'From': 'Karl Hater <hatedragon@hatelook.example.com>',
        'To': '<support@dodgytronic.example.com>',
        'Subject': 'C20261226-42069: Doodgee XGF-90 Warranty Claim',
        'Date': 'Sat, 26 12 2026 10:12:22 +11:00',
        'Message-Id': '<1798240342.593087@hatelook.example.com>',
        '': '\r\nModel: XGF-90-AUS\r\nS/N: 202340X27183B\r\nCategory: Product Issue\r\n\r\nTo Whom It May Concern,\r\n\r\nMy fridge stopped working and now my turkey, cognac and christmas cake is\r\nspoit.\r\n\r\nHow may I get a refund on my fridge and food?\r\n\r\nRegards,\r\n\r\nKarl', # body area
        '__footer': '\r\n'
    },
    {
        '__header': 'From MAILER DAEMON  Sun Dec 27 16:43:34 2026',
        'From': 'Missy <artemis@support.dodgytronic.example.com>',
        'To': 'Karl Hater <hatedragon@hatelook.example.com>',
        'Subject': 'C20261226-42069: Doodgee XGF-90 Warranty Claim',
        'Date': 'Sun, 27 12 2026 16:43:34 +11:00',
        'Message-Id': '<1798350214.112976@dodgytronic.example.com>',
        '': '\r\nSorry, the food is not covered by warranty', # body area
        '__footer': '\r\n'
    },
    {
        '__header': 'From MAILER DAEMON  Sun Dec 27 18:01:29 2026',
        'From': 'Karl Hater <hatedragon@hatelook.example.com>',
        'To': 'Missy <artemis@support.dodgytronic.example.com>',
        'Subject': 'C20261226-42069: Doodgee XGF-90 Warranty Claim',
        'Date': 'Sun, 27 12 2026 18:01:29 +11:00',
        'Message-Id': '<1798354889.140189@hatelook.example.com>',
        '': '\r\nDear Missy,\r\n\r\nI am asking in good faith for my money back for a fridge under warranty and\r\naccording to Consumer Law I am enitled to a full refund, a new turkey, a\r\nbottle of Louis XIII and a christmas cake.\r\n\r\nI will be escalating this matter if I do not a get a satisfactory response\r\nin due course.\r\n\r\nSincerely,\r\n\r\nKarl',
        '__footer': '\r\n'
    },
]
emails_format = {
    'eol': '\r\n',
    'newline': '', # no change
    'sol': '',
    'width_bytes': 80,
       # RFC2822 recommends "78 excluding CRLF", making it 80 in our terms
}

# iCalendar events file
# =====================
# Two-level database
# Tested with Gnome Calendar and Evolution
# Events are on the second level
#
# NOTE: GNOME Calendar seems to require 160-bit UIDs
# PROTIP: "DATE:" is a type override, in this example it specifies
#   an ISO 8601 date without a time
#
calendar = {
    '__type': 'VCALENDAR',
    'CALSCALE': 'GREGORIAN',
    'PRODID': '-//iMWLRDB Test//v0.1//EN',
    'VERSION': '2.0',
    'b087c017b012cf86fc773b93552052b937a2f9d7': { # events are identified by UID
        '__type': 'VEVENT',
        'DTSTAMP': '20260401T000000Z',
        'DTSTART': {'VALUE': 'DATE:20260401'},
        'DTEND': {'VALUE': 'DATE:20260401'},
        'SUMMARY': '10th Anniversary',
        'SEQUENCE': 1,
        'DESCRIPTION': 'we\'ve been together for a helluva long time babe'
    },
    'bfa0749b36e8f3cbc8a412d9f835dca7b1216ead': {
        '__type': 'VEVENT',
        'DTSTAMP': '20260510T000000Z',
        'DTSTART': {'VALUE': 'DATE:20260510'},
        'DTEND': {'VALUE': 'DATE:20260510'},
        'SUMMARY': 'International Mothers\' Day!',
        'SEQUENCE': 1,
        'DESCRIPTION': 'take mum out\\ndon\'t make her angry'
    }, # may be different in your country
    '8f135e6cda0060c654e4d229cc2b46b4f6bb157a': {
        '__type': 'VEVENT',
        'DTSTAMP': '20260906T000000Z',
        'DTSTART': {'VALUE': 'DATE:20260906'},
        'DTEND': {'VALUE': 'DATE:20260906'},
        'SUMMARY': 'Fathers\' Day',
        'DESCRIPTION': 'dad be a bruh'
    } # may be different in your country
}

# TODO: Four-level database for a hypothetical app

# Demonstration of octet-limited width, as opposed to char-limited width
long_string_a = "The long, long Python slithers up the long, long gutter pipe"
long_string_b = "🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍🐍Tour de Python☀️"
