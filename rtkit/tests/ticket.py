from rtkit.tests.common import TestCaseWithFlask
from rtkit.tests.mock import app
from rtkit.resource import RTResource
from rtkit.authenticators import AbstractAuthenticator


class TestCaseTicket(TestCaseWithFlask):
    application = app

    @classmethod
    def setUpClass(cls):
        super(TestCaseTicket, cls).setUpClass()
        cls.resource = RTResource('http://localhost:5000/', None, None, AbstractAuthenticator)

    def test_create_tkt(self):
        message = 'My useless\ntext on\nthree lines.'
        content = {
            'content': {
                'Queue': 1,
                'Subject': 'New Ticket',
                'Text': message.replace('\n', '\n '),
            }
        }
        response = self.resource.post(path='ticket/new', payload=content,)
        self.assertEqual(response.parsed, [[('id', 'ticket/1')]])
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.status, '200 Ok')

    def test_create_tkt_noqueue(self):
        message = 'My useless\ntext on\nthree lines.'
        content = {
            'content': {
                'Queue': 2,
                'Subject': 'New Ticket',
                'Text': message.replace('\n', '\n '),
            }
        }
        response = self.resource.post(path='ticket/new', payload=content,)
        self.assertEqual(response.parsed, [])
        self.assertEqual(response.status_int, 400)
        self.assertEqual(response.status, '400 Could not create ticket. Queue not set')

    def test_create_tkt_noperm(self):
        message = 'My useless\ntext on\nthree lines.'
        content = {
            'content': {
                'Queue': 3,
                'Subject': 'New Ticket',
                'Text': message.replace('\n', '\n '),
            }
        }
        response = self.resource.post(path='ticket/new', payload=content,)
        self.assertEqual(response.parsed, [])
        self.assertEqual(response.status_int, 400)
        self.assertEqual(response.status, "400 No permission to create tickets in the queue '___Admin'")

    def test_read_tkt(self):
        response = self.resource.get(path='ticket/1')
        self.assertEqual(response.parsed, [[
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
        ]])
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.status, '200 Ok')

    def test_read_tkt_notfound(self):
        response = self.resource.get(path='ticket/2')
        self.assertEqual(response.parsed, [])
        self.assertEqual(response.status_int, 404)
        self.assertEqual(response.status, '404 Ticket 2 does not exist')

    def test_update_tkt_syntax(self):
        content = {'content': {'Queue': 3, }}
        response = self.resource.post(path='ticket/1', payload=content,)
        self.assertEqual(response.parsed, [[('queue', 'You may not create requests in that queue.')]])
        self.assertEqual(response.status_int, 409)
        self.assertEqual(response.status, '409 Syntax Error')
