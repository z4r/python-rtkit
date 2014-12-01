import base64
import unittest
from httpretty import httprettified, HTTPretty
from rtkit.resource import RTResource
from rtkit.authenticators import BasicAuthenticator, CookieAuthenticator, QueryStringAuthenticator


class BasicAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.resource = RTResource('http://rtkit.test/', 'USER', 'PASS', BasicAuthenticator)

    @httprettified
    def test_auth(self):
        HTTPretty.register_uri(
            HTTPretty.GET,
            'http://rtkit.test/ticket/1',
            responses=[
                HTTPretty.Response(body='', status=401, www_authenticate='Basic realm="rtkit.test"'),
                HTTPretty.Response(body='RT/3.8.10 200 Ok\n\n# Ticket 1 does not exist.\n\n\n', status=200),
            ]
        )
        self.resource.get(
            path='ticket/1',
            headers={'User-Agent': 'rtkit-ua', }
        )
        self.assertEqual(
            HTTPretty.last_request.headers['authorization'],
            'Basic ' + base64.b64encode('USER:PASS'),
        )


class CookieAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.resource = RTResource('http://rtkit.test/', 'USER', 'PASS', CookieAuthenticator)

    @httprettified
    def test_auth(self):
        HTTPretty.register_uri(
            HTTPretty.POST,
            'http://rtkit.test/',
            body='RT/4.0.5 200 Ok',
            status=200,
            set_cookie='RT_SID_example.com.80=2ec1d46cb1c05fff0fce34ed268e7d26; path=/; HttpOnly',
            transfer_encoding='chunked'
        )
        HTTPretty.register_uri(
            HTTPretty.GET,
            'http://rtkit.test/ticket/1',
            body='RT/3.8.10 200 Ok\n\n# Ticket 1 does not exist.\n\n\n',
            status=200
        )
        self.resource.get(
            path='ticket/1',
            headers={'User-Agent': 'rtkit-ua', }
        )
        self.assertEqual(len(HTTPretty.latest_requests), 2)
        self.assertEqual(HTTPretty.latest_requests[0].path, '/')
        self.assertEqual(HTTPretty.latest_requests[0].method, 'POST')
        self.assertEqual(HTTPretty.latest_requests[0].body, 'user=USER&pass=PASS')
        self.assertEqual(HTTPretty.latest_requests[1].path, '/ticket/1')
        self.assertEqual(HTTPretty.latest_requests[1].method, 'GET')
        self.assertEqual(HTTPretty.latest_requests[1].body, '')


class QueryStringAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.resource = RTResource('http://rtkit.test/', 'USER', 'PASS', QueryStringAuthenticator)

    @httprettified
    def test_auth(self):
        HTTPretty.register_uri(
            HTTPretty.GET,
            'http://rtkit.test/ticket/1',
            responses=[
                HTTPretty.Response(body='RT/3.8.10 200 Ok\n\n# Ticket 1 does not exist.\n\n\n', status=200),
            ]
        )
        self.resource.get(
            path='ticket/1',
            headers={'User-Agent': 'rtkit-ua', }
        )
        self.assertEqual(HTTPretty.latest_requests[0].path, '/ticket/1?user=USER&pass=PASS')
