from itertools import ifilterfalse
import logging
import re
import errors
import forms
import comment
from urllib2 import Request, HTTPError


class RTResource(object):
    def __init__(self, url, username, password, auth, **kwargs):
        self.auth           = auth(username, password, url)
        self.response_cls   = kwargs.get('response_class', RTResponse)
        self.logger         = logging.getLogger('rtkit')

    def get(self, path=None, headers=None):
        return self.request('GET', path, headers=headers)

    def post(self, path=None, payload=None, headers=None):
        return self.request('POST', path, payload, headers)

    def request(self, method, path=None, payload=None, headers=None):
        headers = headers or dict()
        headers.setdefault('Accept', 'text/plain')
        if payload:
            payload = forms.encode(payload, headers)
        self.logger.debug('{0} {1}'.format(method, path))
        self.logger.debug(headers)
        self.logger.debug('%r' % payload)
        req = Request(
            url     = self.auth.url+path,
            data    = payload,
            headers = headers,
        )
        try:
            response = self.auth.open(req)
        except HTTPError as e:
            response = e
        return self.response_cls(req, response)


class RTResponse(object):
    HEADER  = re.compile(r'^RT/(?P<v>.+)\s+(?P<s>(?P<i>\d+).+)')
    COMMENT = re.compile(r'^#\s+.+$')
    SECTION = re.compile(r'^--', re.M|re.U)

    def __init__(self, request, response):
        self.headers    = response.headers
        self.body       = response.read()
        self.status_int = response.code
        self.status     = '{0} {1}'.format(response.code, response.msg)
        self.logger     = logging.getLogger('rtkit')
        self.logger.info(request.get_method())
        self.logger.info(request.get_full_url())
        self.logger.debug('HTTP_STATUS: {0}'.format(self.status))
        r = self.HEADER.match(self.body)
        if r:
            self.status = r.group('s')
            self.status_int = int(r.group('i'))
        else:
            self.logger.error('"{0}" is not valid'.format(self.body))
            self.status = self.body
            self.status_int = 500
        self.logger.debug('%r'%self.body)
        try:
            decoder = self._decode
            if self.status_int == 409:
                decoder = self._decode_comment
            self.parsed = self._parse(self.body, decoder)
        except errors.RTResourceError as e:
            self.parsed = []
            self.status_int = e.status_int
            self.status = '{0} {1}'.format(e.status_int, e.msg)
        self.logger.debug('RESOURCE_STATUS: {0}'.format(self.status))
        self.logger.info(self.parsed)


    @classmethod
    def _parse(cls, body, decoder):
        r""" Return a list of RFC5322-like section
        >>> decode = RTResponse._decode
        >>> body = '''
        ...
        ... # c1
        ... spam: 1
        ... ham: 2,
        ...     3
        ... eggs:'''
        >>> RTResponse._parse(body, decode)
        [[('spam', '1'), ('ham', '2, 3'), ('eggs', '')]]
        >>> RTResponse._parse('# spam 1 does not exist.', decode)
        Traceback (most recent call last):
            ...
        RTNotFoundError: spam 1 does not exist
        >>> RTResponse._parse('# Spam 1 created.', decode)
        [[('id', 'spam/1')]]
        >>> RTResponse._parse('No matching results.', decode)
        []
        >>> decode = RTResponse._decode_comment
        >>> RTResponse._parse('# spam: 1\n# ham: 2', decode)
        [[('spam', '1'), ('ham', '2')]]
        """
        section = cls._build(body)
        if len(section) == 1:
            try:
                comment.check(section[0])
            except comment.RTNoMatch:
                section = ''
            except comment.RTCreated as e:
                section = [['id: {0}'.format(e.id)]]
        return [decoder(lines) for lines in section]

    @classmethod
    def _decode(cls, lines):
        """ Return a list of 2-tuples parsing 'k: v' and skipping comments
        >>> RTResponse._decode(['# c1: c2', 'spam: 1', 'ham: 2, 3', 'eggs:'])
        [('spam', '1'), ('ham', '2, 3'), ('eggs', '')]
        >>> RTResponse._decode(['<!DOCTYPE HTML PUBLIC >', '<html><head>',])
        []
        """
        try:
            lines = ifilterfalse(cls.COMMENT.match, lines)
            return [(k, v.strip(' '))
                for k,v in [l.split(':', 1)
                    for l in lines]]
        except ValueError:
            return []

    @classmethod
    def _decode_comment(cls, lines):
        """ Return a list of 2-tuples parsing '# k: v'
        >>> RTResponse._decode_comment(['# c1: c2', 'spam: 1', 'ham: 2, 3', 'eggs:'])
        [('c1', 'c2')]
        >>>
        """
        lines = filter(cls.COMMENT.match, lines)
        return [(k.strip('# '), v.strip(' '))
            for k,v in [l.split(':', 1)
                for l in lines]]

    @classmethod
    def _build(cls, body):
        """ Build logical lines from a RFC5322-like string
        >>> body = '''RT/1.2.3 200 Ok
        ...
        ... # a
        ...   b
        ... spam: 1
        ...
        ... ham: 2,
        ...     3
        ... --
        ... # c
        ... spam: 4
        ... ham:
        ... --
        ... a -- b
        ... '''
        >>> RTResponse._build(body)
        [['# a b', 'spam: 1', 'ham: 2, 3'], ['# c', 'spam: 4', 'ham:'], ['a -- b']]
        """
        def build_section(section):
            logic_lines = []
            for line in filter(None, section.splitlines()):
                if cls.HEADER.match(line):
                    continue
                if line[0].isspace():
                   logic_lines[-1] += ' '+line.strip(' ')
                else:
                   logic_lines.append(line)
            return logic_lines
        return [build_section(b) for b in cls.SECTION.split(body)]
