class RTResourceError(Exception):
    """ default error class """
    status_int = None

    def __init__(self, msg=None, http_code=None, response=None):
        self.msg = msg or ''
        self.status_int = http_code or self.status_int
        self.response = response
        super(RTResourceError, self).__init__()

    def _get_message(self):
        return self.msg
    def _set_message(self, msg):
        self.msg = msg or ''
    message = property(_get_message, _set_message)

    def __str__(self):
        if self.msg:
            return self.msg
        try:
            return str(self.__dict__)
        except (NameError, ValueError, KeyError), e:
            return 'Unprintable exception %s: %s' \
                % (self.__class__.__name__, str(e))


class RTNotFoundError(RTResourceError):
    status_int = 404


class RTUnknownTypeError(RTResourceError):
    status_int = 400


class RTInvalidError(RTResourceError):
    status_int = 400


class RTValueError(RTResourceError):
    status_int = 400


class RTUnauthorized(RTResourceError):
    status_int = 401


__all__ = [
    'RTUnknownTypeError',
    'RTInvalidError',
    'RTValueError',
    'RTResourceError',
    'RTNotFoundError',
    'RTUnauthorized',
]