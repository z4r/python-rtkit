from restkit.errors import ResourceError as RTResourceError
from restkit.errors import ResourceNotFound, Unauthorized

class RTUnknownTypeError(RTResourceError):
    status_int = 400


class RTInvalidError(RTResourceError):
    status_int = 400


class RTValueError(RTResourceError):
    status_int = 400


class RTNotFoundError(ResourceNotFound):
    pass


class RTUnauthorized(Unauthorized):
    status_int = 401


__all__ = [
    'RTUnknownTypeError',
    'RTInvalidError',
    'RTValueError',
    'RTResourceError',
    'RTNotFoundError',
    'RTUnauthorized',
]