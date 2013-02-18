from rtkit.authenticators import BasicAuthenticator
from rtkit.errors import RTBadConfiguration
from rtkit.resource import RTResource
import unittest


class ResourceTestCase(unittest.TestCase):
    def test_rtrc(self):
        resource = RTResource.from_rtrc(auth=BasicAuthenticator, filename='rtkit/tests/rtrc/right.txt')
        self.assertEqual(resource.auth.username, 'RT_USERNAME')
        self.assertEqual(resource.auth.password, 'RT_PASSWORD')
        self.assertEqual(resource.auth.url, 'http://rt.server//REST/1.0/')

    def test_rtrc_incomplete(self):
        self.assertRaises(RTBadConfiguration, RTResource.from_rtrc, auth=BasicAuthenticator, filename='rtkit/tests/rtrc/incomplete.txt')

    def test_rtrc_notfile(self):
        self.assertRaises(RTBadConfiguration, RTResource.from_rtrc, auth=BasicAuthenticator, filename='rtkit/tests/rtrc/NO.txt')
