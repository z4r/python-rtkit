import urllib
import urllib2
import cookielib

__all__ = ['BasicAuthenticator', 'CookieAuthenticator',]

class AbstractAuthenticator(object):
    def __init__(self, username, password, url, *handlers):
        self.opener     = urllib2.build_opener(*handlers)
        self.username   = username
        self.password   = password
        self.url        = url
        self._logged    = True

    def login(self):
        if self._logged:
            return
        self._login()
        self._logged = True

    def _login(self):
        raise NotImplementedError

    def open(self, request):
        self.login()
        return self.opener.open(request)


class BasicAuthenticator(AbstractAuthenticator):
    def __init__(self, username, password, url):
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, username, password)
        super(BasicAuthenticator, self).__init__(
            username, password, url,
            urllib2.HTTPBasicAuthHandler(passman)
        )


class CookieAuthenticator(AbstractAuthenticator):
    def __init__(self, username, password, url):
        super(CookieAuthenticator, self).__init__(
            username, password, url,
            urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
        )
        self._logged = False

    def _login(self):
        data = {'user': self.username, 'pass': self.password}
        self.opener.open(
            urllib2.Request(self.url, urllib.urlencode(data))
        )