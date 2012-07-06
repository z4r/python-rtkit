from rtkit.tests.common import TestCaseWithFlask
from rtkit.tests.mock import app
from rtkit.resource import RTResource
from rtkit.authenticators import AbstractAuthenticator


class TestCaseRT(TestCaseWithFlask):
    application = app

    @classmethod
    def setUpClass(cls):
        super(TestCaseRT, cls).setUpClass()
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
                'Queue': 'ERR',
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
                'Queue': 'NOPERM',
                'Subject': 'New Ticket',
                'Text': message.replace('\n', '\n '),
            }
        }
        response = self.resource.post(path='ticket/new', payload=content,)
        self.assertEqual(response.parsed, [])
        self.assertEqual(response.status_int, 400)
        self.assertEqual(response.status, "400 No permission to create tickets in the queue '___Admin'")
