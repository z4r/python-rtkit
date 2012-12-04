import unittest
from httpretty import httprettified, HTTPretty
from rtkit.resource import RTResource
from rtkit.authenticators import AbstractAuthenticator


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

    @httprettified
    def assertPost(self, body, parsed, status_int, status, content=None):
        HTTPretty.register_uri(HTTPretty.POST, 'http://rtkit.test/ticket/new', body=body)
        response = self.resource.post(path='ticket/new', payload=content or self.content)
        self.assertEqual(response.parsed, parsed)
        self.assertEqual(response.status_int, status_int)
        self.assertEqual(response.status, status)

    @httprettified
    def assertGet(self, body, parsed, status_int, status):
        HTTPretty.register_uri(HTTPretty.GET, 'http://rtkit.test/ticket/1', body=body)
        response = self.resource.get(path='ticket/1')
        self.assertEqual(response.parsed, parsed)
        self.assertEqual(response.status_int, status_int)
        self.assertEqual(response.status, status)

    def test_create_tkt(self):
        self.assertPost(
            body='RT/3.8.10 200 Ok\n\n# Ticket 1 created.\n\n',
            parsed=[[('id', 'ticket/1')]],
            status_int=200,
            status='200 Ok',
        )

    def test_create_tkt_noqueue(self):
        self.assertPost(
            body='RT/3.8.10 200 Ok\n\n# Could not create ticket.\n# Could not create ticket. Queue not set\n\n',
            parsed=[],
            status_int=400,
            status='400 Could not create ticket. Queue not set',
        )

    def test_create_tkt_noperm(self):
        self.assertPost(
            body='RT/3.8.10 200 Ok\n\n# Could not create ticket.\n# No permission to create tickets in the queue \'___Admin\'\n\n',
            parsed=[],
            status_int=400,
            status='400 No permission to create tickets in the queue \'___Admin\'',
        )

    def test_read_tkt(self):
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
        )

    def test_read_tkt_notfound(self):
        self.assertPost(
            body='RT/3.8.10 200 Ok\n\n# Ticket 1 does not exist.\n\n\n',
            parsed=[],
            status_int=404,
            status='404 Ticket 1 does not exist',
        )

    def test_read_tkt_credentials(self):
        self.assertPost(
            body='RT/3.8.10 401 Credentials required\n',
            parsed=[],
            status_int=401,
            status='401 Credentials required',
        )

    def test_update_tkt_syntax(self):
        self.assertPost(
            body='RT/3.8.10 409 Syntax Error\n\n# queue: You may not create requests in that queue.\n\n',
            parsed=[[('queue', 'You may not create requests in that queue.')]],
            status_int=409,
            status='409 Syntax Error',
            content={'content': {'Queue': 3, }}
        )
