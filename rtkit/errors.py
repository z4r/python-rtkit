import re
from restkit.errors import ResourceError as RTResourceError
from restkit.errors import ResourceNotFound as RTNotFoundError

class RTUnknownTypeError(RTResourceError):
    pass


class RTInvalidError(RTResourceError):
    pass


class RTValueError(RTResourceError):
    pass


__all__ = [
    'RTUnknownTypeError',
    'RTInvalidError',
    'RTNotFoundError',
    'RTValueError',
    'RTResourceError',
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

def parse(line):
    '''Parse and Dispatch RT errors
    >>> e = parse('# Unknown object type: spam')
    >>> isinstance(e, RTUnknownTypeError)
    True
    >>> e.msg
    'Unknown object type: spam'
    >>> e = parse("# Invalid object specification: 'spam'")
    >>> isinstance(e, RTInvalidError)
    True
    >>> e.msg
    "Invalid object specification: 'spam'"
    >>> e = parse('# spam 1 does not exist.')
    >>> isinstance(e, RTNotFoundError)
    True
    >>> e.msg
    'spam 1 does not exist'
    >>> e = parse('# No spam named ham exists.')
    >>> isinstance(e, RTNotFoundError)
    True
    >>> e.msg
    'No spam named ham exists'
    >>> e = parse('# Objects of type eggs must be specified by numeric id.')
    >>> isinstance(e, RTValueError)
    True
    >>> e.msg
    'Objects of type eggs must be specified by numeric id'
    '''
    msg = line.lstrip('# ').rstrip('.')
    m = UNKNOWN.match(line)
    if m:
        return RTUnknownTypeError(msg)
    m = INVALID.match(line)
    if m:
        return RTInvalidError(msg)
    m = NOTFOUND.match(line)
    if m:
        return RTNotFoundError(msg)
    m = NAMED_NOTFOUND.match(line)
    if m:
        return RTNotFoundError(msg)
    m = NAN.match(line)
    if m:
        return RTValueError(msg)
