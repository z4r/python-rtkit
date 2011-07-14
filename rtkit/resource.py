from itertools import ifilterfalse
import logging
import re
from restkit import Resource, Response
import errors
import forms
import comment

class RTResource(Resource):
    BOUNDARY = 'xXXxXXyYYzzz'
    def __init__(self, uri, **kwargs):
        kwargs['response_class'] = RTResponse
        super(RTResource, self).__init__(uri, **kwargs)
        self.logger = logging.getLogger('rtkit')

    def request(self, method, path=None, payload=None, headers=None, **kwargs):
        headers = headers or dict()
        headers.setdefault('Accept', 'text/plain')
        if payload:
            payload = forms.encode(payload, self.BOUNDARY, headers)
        self.logger.debug('{0} {1}'.format(method, path))
        self.logger.debug(headers)
        self.logger.debug('%r' % payload)
        return super(RTResource, self).request(
            method,
            path=path,
            payload=payload,
            headers=headers,
            **kwargs
        )


class RTResponse(Response):
    HEADER_PATTERN = '^RT/(?P<v>\d+\.\d+\.\d+)\s+(?P<s>(?P<i>\d+).+)'
    HEADER = re.compile(HEADER_PATTERN)
    COMMENT_PATTERN = '^#\s+.+$'
    COMMENT = re.compile(COMMENT_PATTERN)

    def __init__(self, connection, request, resp):
        super(RTResponse, self).__init__(connection, request, resp)
        self.logger = logging.getLogger('rtkit')
        self.logger.info('HTTP_STATUS: {0}'.format(self.status))
        body = self._body.read()
        r = self.HEADER.match(body)
        if r:
            self.version = tuple([int(v) for v in r.group('v').split('.')])
            self.status = r.group('s')
            self.status_int = int(r.group('i'))
        else:
            self.logger.error('"{0}" is not valid'.format(body))
            self.status = body
            self.status_int = 500
        self.logger.debug('%r'%body)
        try:
            decode = self._decode
            if self.status_int == 409:
                decode = self._decode_comment
            self.parsed = self._parse(body, decode)
        except errors.RTResourceError as e:
            self.parsed = []
            self.status_int = e.status_int
            self.status = '{0} {1}'.format(e.status_int, e.msg)
        self.logger.info('RESOURCE_STATUS: {0}'.format(self.status))

    @classmethod
    def _parse(cls, body, decode):
        r'''Return a list of RFC5322-like section
        >>> decode = RTResponse._decode
        >>> body = """
        ...
        ... # c1
        ... spam: 1
        ... ham: 2,
        ...     3
        ... eggs:"""
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
        '''
        section = cls._build(body)
        if len(section) == 1:
            try:
                comment.check(section[0])
            except comment.RTNoMatch:
                section = ''
            except comment.RTCreated as e:
                section = [['id: {0}'.format(e.id)]]
        return [decode(lines) for lines in section]

    @classmethod
    def _decode(cls, lines):
        '''Return a list of 2-tuples parsing 'k: v' and skipping comments
        >>> RTResponse._decode(['# c1: c2', 'spam: 1', 'ham: 2, 3', 'eggs:'])
        [('spam', '1'), ('ham', '2, 3'), ('eggs', '')]
        >>>
        '''
        lines = ifilterfalse(cls.COMMENT.match, lines)
        return [(k, v.strip(' '))
            for k,v in [l.split(':', 1)
                for l in lines]]

    @classmethod
    def _decode_comment(cls, lines):
        '''Return a list of 2-tuples parsing '# k: v'
        >>> RTResponse._decode_comment(['# c1: c2', 'spam: 1', 'ham: 2, 3', 'eggs:'])
        [('c1', 'c2')]
        >>>
        '''
        lines = filter(cls.COMMENT.match, lines)
        return [(k.strip('# '), v.strip(' '))
            for k,v in [l.split(':', 1)
                for l in lines]]

    @classmethod
    def _build(cls, body):
        '''Build logical lines from a RFC5322-like string
        >>> body = """RT/1.2.3 200 Ok
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
        ... """
        >>> RTResponse._build(body)
        [['# a b', 'spam: 1', 'ham: 2, 3'], ['# c', 'spam: 4', 'ham:']]
        '''
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
        return [build_section(b) for b in body.split('--')]