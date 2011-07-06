from itertools import ifilterfalse
import logging
import re

from restkit import Resource, Response
import errors

USER_AGENT = 'pyRTkit/{0}'.format('0.0.1')

class RTResource(Resource):
    def __init__(self, uri, **kwargs):
        kwargs['response_class'] = RTResponse
        super(RTResource, self).__init__(uri, **kwargs)
        self.logger = logging.getLogger('rtkit')

    def request(self, method, path=None, payload=None, headers=None, **kwargs):
        headers = headers or dict()
        headers.setdefault('Accept', 'text/plain')
        headers.setdefault('User-Agent', USER_AGENT)
        if payload and not hasattr(payload, 'read') \
            and not isinstance(payload, basestring):
            payload = self.encode(payload)
            headers.setdefault('Content-Type',
                               'application/x-www-form-urlencoded')
        self.logger.debug('{0} {1}'.format(method, path))
        self.logger.debug(headers)
        self.logger.debug('%r'%payload)
        return super(RTResource, self).request(
            method,
            path=path,
            payload=payload,
            headers=headers,
            **kwargs
        )

    @staticmethod
    def encode(payload):
        r'''Encode a dictionary into a valid RT query string
        >>> payload = {'spam': 1, 'ham':2, 'eggs':3, }
        >>> RTResource.encode(payload)
        u'content=eggs: 3\nham: 2\nspam: 1\n'
        '''
        pstr = ['{0}: {1}'.format(k,v) for k,v in payload.iteritems()]
        return u'content={0}\n'.format('\n'.join(pstr))


class RTResponse(Response):
    HEADER_PATTERN = '^RT/(?P<v>\d+\.\d+\.\d+)\s+(?P<s>(?P<i>\d+)\s+\w+)'
    HEADER = re.compile(HEADER_PATTERN)
    COMMENT_PATTERN = '^#\s+'
    COMMENT = re.compile(COMMENT_PATTERN)

    def __init__(self, connection, request, resp):
        self.logger = logging.getLogger('rtkit')
        if resp.status_int == 200:
            resp_header = resp.body.next()
            self.logger.debug(resp_header)
            r = self.HEADER.match(resp_header)
            if r:
                resp.version = tuple([int(v) for v in r.group('v').split('.')])
                resp.status = r.group('s')
                resp.status_int = int(r.group('i'))
            else:
                resp.status = resp_header
                resp.status_int = 500
        super(RTResponse, self).__init__(connection, request, resp)

    @property
    def single(self):
        return self._single(self.body_string())

    @property
    def search(self):
        return self._search(self.body_string())

    @property
    def detailed_query(self):
        return self._detailed_search(self.body_string())

    @classmethod
    def _single(cls, body):
        '''Return an 2-tuple list representing resourse attributes
        >>> body = """
        ...
        ... spam: 1
        ... ham: 2,
        ...     3
        ... eggs:"""
        >>> RTResponse._single(body)
        [('spam', '1'), ('ham', '2, 3'), ('eggs', '')]
        >>> body = '# spam 1 does not exist.'
        >>> RTResponse._single(body)
        Traceback (most recent call last):
            ...
        ResourceNotFound: spam 1 does not exist
        '''
        lines = cls._build_lines(body)
        if lines and cls.COMMENT.match(lines[0]):
            raise errors.parse(lines[0])
        return cls._decode(lines)

    @classmethod
    def _search(cls, body):
        '''Return a tuple list representing id, name of matching resourses
        >>> body = """
        ...
        ... 1: spam
        ... 2: ham
        ... 3: eggs"""
        >>> RTResponse._search(body)
        [('1', 'spam'), ('2', 'ham'), ('3', 'eggs')]
        >>> body = 'No matching results.'
        >>> RTResponse._search(body)
        []
        '''
        lines = cls._build_lines(body)
        if errors.NO_MATCHING.match(lines[0]):
            return []
        return cls._decode(lines)

    @classmethod
    def _detailed_search(cls, body):
        '''Return a list of decoded lines representing matching resourses
        >>> body = """
        ... spam: 1
        ... ham: 2
        ... --
        ... spam: 4
        ... ham: 5"""
        >>> RTResponse._detailed_search(body)
        [[('spam', '1'), ('ham', '2')], [('spam', '4'), ('ham', '5')]]
        >>> body = 'No matching results.'
        >>> RTResponse._detailed_search(body)
        []
        '''
        lines_list = [cls._build_lines(b) for b in body.split('--')]
        if errors.NO_MATCHING.match(lines_list[0][0]):
            return []
        return [cls._decode(lines) for lines in lines_list]

    @classmethod
    def _decode(cls, lines):
        '''Return a 2-tuples list skipping comments
        >>> RTResponse._decode(['# c1 c2', 'spam: 1', 'ham: 2, 3', 'eggs:'])
        [('spam', '1'), ('ham', '2, 3'), ('eggs', '')]
        '''
        lines = ifilterfalse(cls.COMMENT.match, lines)
        return [(k, v.strip(' ')) for k,v in [l.split(':', 1) for l in lines]]

    @staticmethod
    def _build_lines(body):
        '''Build logical lines as RFC822
        >>> body = """
        ... # c1
        ...   c2
        ... spam: 1
        ...
        ... ham: 2,
        ...     3  
        ... eggs:"""
        >>> RTResponse._build_lines(body)
        ['# c1 c2', 'spam: 1', 'ham: 2, 3', 'eggs:']
        '''
        logic_lines = []
        for line in filter(None, body.splitlines()):
            if line[0].isspace():
               logic_lines[-1] += ' '+line.strip(' ')
            else:
               logic_lines.append(line)
        return logic_lines