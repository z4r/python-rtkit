import re
from .errors import *

UNKNOWN_PATTERN = '# Unknown object type: (?P<t>.+)'
UNKNOWN = re.compile(UNKNOWN_PATTERN)
INVALID_PATTERN = '# Invalid object specification: \'(?P<t>.+)\''
INVALID = re.compile(INVALID_PATTERN)
NOTFOUND_PATTERN = '# (?P<t>\w+) (?P<r>\d+) does not exist.'
NOTFOUND = re.compile(NOTFOUND_PATTERN)
NAMED_NOTFOUND_PATTERN = '# No (?P<t>\w+) named (?P<r>\w+) exists.'
NAMED_NOTFOUND = re.compile(NAMED_NOTFOUND_PATTERN)
NAN_PATTERN = '# Objects of type (?P<t>\w+) must be specified by numeric id.'
NAN = re.compile(NAN_PATTERN)
NOT_CREATED_PATTERN = '# Could not create (?P<t>\w+).'
NOT_CREATED = re.compile(NOT_CREATED_PATTERN)
NO_MATCHING_PATTERN = 'No matching results.'
NO_MATCHING = re.compile(NO_MATCHING_PATTERN)
CREATED_PATTERN = '# (?P<t>\w+) (?P<r>\d+) created.'
CREATED = re.compile(CREATED_PATTERN)
UNAUTHORIZED_PATTERN = '# You are not allowed to modify (?P<t>\w+) (?P<r>\w+).'
UNAUTHORIZED = re.compile(UNAUTHORIZED_PATTERN)


class RTCreated(Exception):
    """Created Exception"""
    def __init__(self, msg):
        m = CREATED.match(msg)
        self.id = '{0}/{1}'.format(m.group('t').lower(), m.group('r'))


class RTNoMatch(Exception):
    """No Match Exception"""
    pass


def _clear(section, lineno=0):
    return section[lineno].lstrip('# ').rstrip('.')


def _pass(section, lineno=0):
    return section[lineno]


def check(section):
    """Parse and Dispatch Errors

    .. seealso:: The :py:mod:`rtkit.errors` module

    .. doctest::

        >>> check(['# Unknown object type: spam'])
        Traceback (most recent call last):
                ...
        RTUnknownTypeError: Unknown object type: spam
        >>> check(["# Invalid object specification: 'spam'"])
        Traceback (most recent call last):
                ...
        RTInvalidError: Invalid object specification: 'spam'
        >>> check(['# spam 1 does not exist.'])
        Traceback (most recent call last):
                ...
        RTNotFoundError: spam 1 does not exist
        >>> check(['# No spam named ham exists.'])
        Traceback (most recent call last):
                ...
        RTNotFoundError: No spam named ham exists
        >>> check(['# Objects of type eggs must be specified by numeric id.'])
        Traceback (most recent call last):
                ...
        RTValueError: Objects of type eggs must be specified by numeric id
        >>> check(['No matching results.'])
        Traceback (most recent call last):
                ...
        RTNoMatch: No matching results
        >>> check(['# Could not create ticket.', '# Could not create ticket. Queue not set'])
        Traceback (most recent call last):
                ...
        RTInvalidError: Could not create ticket. Queue not set
        >>> try:
        ...     check(['# Ticket 1 created.'])
        ... except RTCreated as e:
        ...     e.id
        'ticket/1'
        >>> check(['# You are not allowed to modify ticket 2.'])
        Traceback (most recent call last):
                ...
        RTUnauthorized: You are not allowed to modify ticket 2
    """
    def _incheck(section, e):
        m = e[0].match(section[0])
        if m:
            raise e[1](e[2](section, e[3]))
    for e in PARSING_TABLE:
        _incheck(section, e)

# compiled_pattern, error_class, method, line_msg
PARSING_TABLE = (
    (UNKNOWN, RTUnknownTypeError, _clear, 0),
    (INVALID, RTInvalidError, _clear, 0),
    (NOTFOUND, RTNotFoundError, _clear, 0),
    (NAMED_NOTFOUND, RTNotFoundError, _clear, 0),
    (NO_MATCHING, RTNoMatch, _clear, 0),
    (NAN, RTValueError, _clear, 0),
    (NOT_CREATED, RTInvalidError, _clear, 1),
    (CREATED, RTCreated, _pass, 0),
    (UNAUTHORIZED, RTUnauthorized, _clear, 0)
)
