from restkit.errors import ResourceError as RTResourceError
from restkit.errors import ResourceNotFound

class RTUnknownTypeError(RTResourceError):
    status_int = 400


class RTInvalidError(RTResourceError):
    status_int = 400


class RTValueError(RTResourceError):
    status_int = 400

class RTNotFoundError(ResourceNotFound):
    pass


__all__ = [
    'RTUnknownTypeError',
    'RTInvalidError',
    'RTValueError',
    'RTResourceError',
    'RTNotFoundError',
]