from collections import namedtuple
import unittest
from httpretty import httprettified, HTTPretty
from rtkit.resource import RTResource
from rtkit.authenticators import AbstractAuthenticator

Expected = namedtuple('Expected', 'req_body req_headers parsed status_int status')


class TktTestCase(unittest.TestCase):
    def setUp(self):
        self.resource = RTResource('http://rtkit.test/', None, None, AbstractAuthenticator)
        self.content = {
            'content': {
                'Queue': 1,
                'Subject': 'New Ticket',
                'Text': 'My useless\ntext on\nthree lines.',
            }
        }
        self.req_body = 'content=Queue: 1\nText: My+useless%0A+text+on%0A+three+lines.\nSubject: New Ticket'
        self.req_headers_get = {
            'connection': 'close',
            'user-agent': 'rtkit-ua',
            'host': 'rtkit.test',
            'accept': 'text/plain',
            'accept-encoding': 'identity',
        }
        self.req_headers_post = self.req_headers_get.copy()
        self.req_headers_post.update({
            'content-length': '80',
            'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
        })

    @httprettified
    def test_http_error(self):
        HTTPretty.register_uri(HTTPretty.GET, 'http://rtkit.test/:GET:', status=404, body='Not Found')
        response = self.resource.get(':GET:', headers={'User-Agent': 'rtkit-ua', })
        self.assertEqual(response.parsed, [[]])
        self.assertEqual(response.status_int, 500)
        self.assertEqual(response.status, 'Not Found')

    @httprettified
    def assertPost(self, body, expected, content=None):
        HTTPretty.register_uri(HTTPretty.POST, 'http://rtkit.test/:POST:', body=body)
        response = self.resource.post(
            path=':POST:',
            payload=content or self.content,
            headers={'User-Agent': 'rtkit-ua', }
        )
        self.assertEqual(response.parsed, expected.parsed)
        self.assertEqual(response.status_int, expected.status_int)
        self.assertEqual(response.status, expected.status)
        self.assertEqual(HTTPretty.last_request.method, HTTPretty.POST)
        self.assertEqual(HTTPretty.last_request.path, '/:POST:')
        self.assertEqual(HTTPretty.last_request.body, expected.req_body)
        self.assertEqual(dict(HTTPretty.last_request.headers), expected.req_headers)

    @httprettified
    def assertGet(self, body, expected):
        HTTPretty.register_uri(HTTPretty.GET, 'http://rtkit.test/:GET:', body=body)
        response = self.resource.get(
            path=':GET:',
            headers={'User-Agent': 'rtkit-ua', }
        )
        self.assertEqual(response.parsed, expected.parsed)
        self.assertEqual(response.status_int, expected.status_int)
        self.assertEqual(response.status, expected.status)
        self.assertEqual(HTTPretty.last_request.method, HTTPretty.GET)
        self.assertEqual(HTTPretty.last_request.path, '/:GET:')
        self.assertEqual(HTTPretty.last_request.body, expected.req_body)
        self.assertEqual(dict(HTTPretty.last_request.headers), expected.req_headers)

    def test_create_tkt(self):
        expected = Expected(
            parsed=[[('id', 'ticket/1')]],
            status_int=200,
            status='200 Ok',
            req_body=self.req_body,
            req_headers=self.req_headers_post,
        )
        self.assertPost(
            body='RT/3.8.10 200 Ok\n\n# Ticket 1 created.\n\n',
            expected=expected,
        )

    def test_create_tkt_noqueue(self):
        expected = Expected(
            parsed=[],
            status_int=400,
            status='400 Could not create ticket. Queue not set',
            req_body=self.req_body,
            req_headers=self.req_headers_post,
        )
        self.assertPost(
            body='RT/3.8.10 200 Ok\n\n# Could not create ticket.\n# Could not create ticket. Queue not set\n\n',
            expected=expected,
        )

    def test_create_tkt_noperm(self):
        expected = Expected(
            parsed=[],
            status_int=400,
            status='400 No permission to create tickets in the queue \'___Admin\'',
            req_body=self.req_body,
            req_headers=self.req_headers_post,
        )
        self.assertPost(
            body='RT/3.8.10 200 Ok\n\n# Could not create ticket.\n# No permission to create tickets in the queue \'___Admin\'\n\n',
            expected=expected,
        )

    def test_read_tkt(self):
        expected = Expected(
            parsed=[[
                ('id', 'ticket/1'),
                ('Queue', 'General'),
                ('Owner', 'Nobody'),
                ('Creator', 'pyrtkit'),
                ('Subject', 'pyrt-create4'),
                ('Status', 'open'),
                ('Priority', '5'),
                ('InitialPriority', '0'),
                ('FinalPriority', '0'),
                ('Requestors', ''),
                ('Cc', ''),
                ('AdminCc', ''),
                ('Created', 'Sun Jul 03 10:48:57 2011'),
                ('Starts', 'Not set'),
                ('Started', 'Not set'),
                ('Due', 'Not set'),
                ('Resolved', 'Not set'),
                ('Told', 'Wed Jul 06 12:58:00 2011'),
                ('LastUpdated', 'Thu Jul 07 14:42:32 2011'),
                ('TimeEstimated', '0'),
                ('TimeWorked', '25 minutes'),
                ('TimeLeft', '0'),
            ]],
            status_int=200,
            status='200 Ok',
            req_body='',
            req_headers=self.req_headers_get,
        )
        self.assertGet(
            body='''RT/3.8.10 200 Ok

id: ticket/1
Queue: General
Owner: Nobody
Creator: pyrtkit
Subject: pyrt-create4
Status: open
Priority: 5
InitialPriority: 0
FinalPriority: 0
Requestors:
Cc:
AdminCc:
Created: Sun Jul 03 10:48:57 2011
Starts: Not set
Started: Not set
Due: Not set
Resolved: Not set
Told: Wed Jul 06 12:58:00 2011
LastUpdated: Thu Jul 07 14:42:32 2011
TimeEstimated: 0
TimeWorked: 25 minutes
TimeLeft: 0


''',
            expected=expected,
        )

    def test_read_tkt_notfound(self):
        expected = Expected(
            parsed=[],
            status_int=404,
            status='404 Ticket 1 does not exist',
            req_body='',
            req_headers=self.req_headers_get,
        )
        self.assertGet(
            body='RT/3.8.10 200 Ok\n\n# Ticket 1 does not exist.\n\n\n',
            expected=expected,
        )

    def test_read_tkt_credentials(self):
        expected = Expected(
            parsed=[],
            status_int=401,
            status='401 Credentials required',
            req_body='',
            req_headers=self.req_headers_get,
        )
        self.assertGet(
            body='RT/3.8.10 401 Credentials required\n',
            expected=expected,
        )

    def test_update_tkt_syntax_error(self):
        self.req_headers_post.update({'content-length': '16'})
        expected = Expected(
            parsed=[[('queue', 'You may not create requests in that queue.')]],
            status_int=409,
            status='409 Syntax Error',
            req_body='content=Queue: 3',
            req_headers=self.req_headers_post,
        )
        self.assertPost(
            body='RT/3.8.10 409 Syntax Error\n\n# queue: You may not create requests in that queue.\n\n',
            expected=expected,
            content={'content': {'Queue': 3, }}
        )

    def test_tkt_comment_with_attach(self):
        self.req_headers_post.update({
            'content-length': '760',
            'content-type': 'multipart/form-data; boundary=xXXxXXyYYzzz',
        })
        expected = Expected(
            parsed=[[]],
            status_int=200,
            status='200 Ok',
            req_body='--xXXxXXyYYzzz\r\nContent-Disposition: form-data; name="content"\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 77\r\n\r\nAction: comment\nText: Comment with attach\nAttachment: x1.txt, x2.txt, 1x1.gif\r\n--xXXxXXyYYzzz\r\nContent-Disposition: form-data; name="attachment_2"; filename="rtkit/tests/attach/x2.txt"\r\nContent-Type: text/plain\r\nContent-Length: 15\r\n\r\nHello World!\n2\n\r\n--xXXxXXyYYzzz\r\nContent-Disposition: form-data; name="attachment_1"; filename="rtkit/tests/attach/x1.txt"\r\nContent-Type: text/plain\r\nContent-Length: 15\r\n\r\nHello World!\n1\n\r\n--xXXxXXyYYzzz\r\nContent-Disposition: form-data; name="attachment_3"; filename="rtkit/tests/attach/1x1.gif"\r\nContent-Type: image/gif\r\nContent-Length: 35\r\n\r\nGIF87a\x01\x00\x01\x00\x80\x00\x00\xcc\xcc\xcc\x96\x96\x96,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;\r\n--xXXxXXyYYzzz--\r\n',
            req_headers=self.req_headers_post,
        )
        self.assertPost(
            body='RT/3.8.10 200 Ok\n\n# Message recorded\n\n',
            expected=expected,
            content={
                'content': {
                    'Action': 'comment',
                    'Text': 'Comment with attach',
                    'Attachment': 'x1.txt, x2.txt, 1x1.gif',
                },
                'attachment_1': file('rtkit/tests/attach/x1.txt'),
                'attachment_2': file('rtkit/tests/attach/x2.txt'),
                'attachment_3': file('rtkit/tests/attach/1x1.gif'),
            }
        )

    def test_read_tkt_comment(self):
        expected = Expected(
            parsed=[[
                ('id', '2831'),
                ('Ticket', '216'),
                ('TimeTaken', '0'),
                ('Type', 'Create'),
                ('Field', ''),
                ('OldValue', ''),
                ('NewValue', ''),
                ('Data', ''),
                ('Description', 'Ticket created by john.foo'),
                ('Content', 'this is a\nmultiline\nticket'),
                ('Creator', 'john.foo'),
                ('Created', '2013-02-14 18:00:45'),
                ('Attachments', '\n1315: untitled (38b)')
            ]],
            status_int=200,
            status='200 Ok',
            req_body='',
            req_headers=self.req_headers_get,
        )
        self.assertGet(
            body='''RT/4.0.5-116-g591e06a 200 Ok

# 2/2 (id/2831/total)

id: 2831
Ticket: 216
TimeTaken: 0
Type: Create
Field:
OldValue:
NewValue:
Data:
Description: Ticket created by john.foo

Content: this is a
         multiline
         ticket


Creator: john.foo
Created: 2013-02-14 18:00:45

Attachments:
             1315: untitled (38b)
''',
            expected=expected,
        )
