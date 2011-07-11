import re
from restkit.errors import ResourceError as RTResourceError
from restkit.errors import ResourceNotFound

class RTUnknownTypeError(RTResourceError):
    status_int = 400


class RTInvalidError(RTResourceError):
    status_int = 400


class RTValueError(RTResourceError):
    status_int = 400


class RTCreated(Exception):
    def __init__(self, msg):
        m = CREATED.match('# '+msg+'.')
        self.id = '{0}/{1}'.format(m.group('t').lower(), m.group('r'))


__all__ = [
    'RTUnknownTypeError',
    'RTInvalidError',
    'RTValueError',
    'RTResourceError',
    'ResourceNotFound',
]

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

# compiled_pattern, error_class, match_line, msg_line
PARSING_TABLE = (
    (UNKNOWN, RTUnknownTypeError),
    (INVALID, RTInvalidError),
    (NOTFOUND, ResourceNotFound),
    (NAMED_NOTFOUND, ResourceNotFound),
    (NO_MATCHING, ResourceNotFound),
    (NAN, RTValueError),
    (NOT_CREATED, RTInvalidError),
    (CREATED, RTCreated),
)

def check(section):
    '''Parse and Dispatch RT errors
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
    ResourceNotFound: spam 1 does not exist
    >>> check(['# No spam named ham exists.'])
    Traceback (most recent call last):
            ...
    ResourceNotFound: No spam named ham exists
    >>> check(['# Objects of type eggs must be specified by numeric id.'])
    Traceback (most recent call last):
            ...
    RTValueError: Objects of type eggs must be specified by numeric id
    '''
    def _incheck(line, e):
        m = e[0].match(line)
        if m:
            raise e[1](line.lstrip('# ').rstrip('.'))
    for e in PARSING_TABLE:
        _incheck(section[0], e)
