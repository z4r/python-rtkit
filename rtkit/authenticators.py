import urllib
import urllib2
import cookielib
import base64

__all__ = ['BasicAuthenticator', 'CookieAuthenticator',]

class AbstractAuthenticator(object):
    def __init__(self, username, password, *handlers):
        self.opener = urllib2.build_opener(*handlers)
        self.username = username
        self.password = password

    def login(self, uri):
        pass

    def open(self, request):
        return self.opener.open(request)


class BasicAuthenticator(AbstractAuthenticator):
    def __init__(self, username, password):
        super(BasicAuthenticator, self).__init__(username, password)
        encoded_auth = base64.encodestring('%s:%s' % (username, password))
        self.auth_header = {
            'authorization' : "basic %s" % encoded_auth.strip()
        }

    def open(self, request):
        request.headers.update(self.auth_header)
        return super(BasicAuthenticator, self).open(request)


class CookieAuthenticator(AbstractAuthenticator):
    def __init__(self, username, password):
        super(CookieAuthenticator, self).__init__(
            username, password,
            urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
        )
        self._login = False

    def login(self, uri):
        if self._login:
            return
        data = {'user': self.username, 'pass': self.password}
        super(CookieAuthenticator, self).open(
            urllib2.Request(uri, urllib.urlencode(data))
        )
        self._login = True