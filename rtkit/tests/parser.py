import unittest
from rtkit.parser import RTParser


class ParserTestCase(unittest.TestCase):
    def test_parse_syntax_err(self):
        body = '''RT/3.6.6 409 Syntax Error

# Syntax error.

Queue: Vulnerabilities
CF-Priority: Low -Needs to be completed in > 30
>> CF-Is This Maintenance?: Not_maintenance
CF-Device or Area: My Device
Owner: jgreen
Text: I'm a thing
CF-Vulnerability Risk: Low
CF-Time Estimated: Days
CF-CVSS Score: 2.6
Subject: Test Vulnerability for Script Dev
'''
        parsed = RTParser.parse(body, RTParser.decode_comment)
        self.assertEqual(parsed, [[('CF-Is This Maintenance?', 'Not_maintenance')]])

    def test_parse_kw_syntax_err(self):
        body = '''RT/3.8.10 409 Syntax Error

# queue: You may not create requests in that queue.
'''
        parsed = RTParser.parse(body, RTParser.decode_comment)
        self.assertEqual(parsed, [[('queue', 'You may not create requests in that queue.')]])

    def test_vertical_tab(self):
        body = '''RT/3.8.7 200 Ok
Field: first line
       second\vline
       third line
'''
        parsed = RTParser.parse(body, RTParser.decode)
        self.assertEqual(parsed, [[('Field', 'first line\nsecond\x0bline\nthird line')]])
