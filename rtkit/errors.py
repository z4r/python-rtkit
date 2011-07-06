import re
from restkit.errors import ResourceError as RTResourceError
from restkit.errors import ResourceNotFound

class RTUnknownTypeError(RTResourceError):
    pass


class RTInvalidError(RTResourceError):
    pass


class RTValueError(RTResourceError):
    pass


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
NO_MATCHING_PATTERN = 'No matching results.'
NO_MATCHING = re.compile(NO_MATCHING_PATTERN)

# compiled_pattern, error_class, match_line, msg_line
ERROR_TABLE = (
    (UNKNOWN, RTUnknownTypeError, 0, 0,),
    (INVALID, RTInvalidError, 0, 0,),
    (NOTFOUND, ResourceNotFound, 0, 0,),
    (NAMED_NOTFOUND, ResourceNotFound, 0, 0,),
    (NO_MATCHING, ResourceNotFound, 0, 0,),
    (NAN, RTValueError, 0, 0,),
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
    def _incheck(section, e):
        m = e[0].match(section[e[2]])
        if m:
            raise e[1](section[e[3]].lstrip('# ').rstrip('.'))
    for e in ERROR_TABLE:
        _incheck(section, e)
