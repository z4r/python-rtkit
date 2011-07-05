import re
from restkit import Resource, Response
import errors
from ordereddict import OrderedDict

USER_AGENT = 'pyRTkit/{0}'.format('0.0.1')

class RTResource(Resource):
    def __init__(self, uri, **kwargs):
        kwargs['response_class'] = RTResponse
        super(RTResource, self).__init__(uri, **kwargs)

    def request(self, method, path=None, payload=None, headers=None, **kwargs):
        headers = headers or dict()
        headers.setdefault('Accept', 'text/plain')
        headers.setdefault('User-Agent', USER_AGENT)
        if payload:
            if not hasattr(payload, 'read') and not isinstance(payload, basestring):
                payload = self.encode(payload)
                headers.setdefault('Content-Type', 'application/x-www-form-urlencoded')
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
    HEADER_PATTERN = '^RT/(?P<version>\d+\.\d+\.\d+)\s+(?P<status>(?P<status_int>\d+)\s+\w+)'
    HEADER = re.compile(HEADER_PATTERN)

    def __init__(self, connection, request, resp):
        if resp.status_int == 200:
            resp_header = resp.body.next()
            r = self.HEADER.match(resp_header)
            if r:
                resp.version    = tuple([int(v) for v in r.group('version').split('.')])
                resp.status     = r.group('status')
                resp.status_int = int(r.group('status_int'))
            else:
                resp.status     = resp_header
                resp.status_int = 500
        super(RTResponse, self).__init__(connection, request, resp)

    @property
    def single(self):
        return self._single(self.body_string())

    @property
    def query(self):
        return self._query(self.body_string())

    @property
    def detailed_query(self):
        return self._detailed_query(self.body_string())

    @classmethod
    def _single(cls, body):
        '''Return an ordered dictionary representing a single resourse's attributes
        >>> body = """
        ...
        ... spam: 1
        ... ham: 2,
        ...     3
        ... eggs:"""
        >>> RTResponse._single(body)
        OrderedDict([('spam', '1'), ('ham', '2,3'), ('eggs', '')])
        >>> body = '# spam 1 does not exist.'
        >>> RTResponse._single(body)
        Traceback (most recent call last):
            ...
        ResourceNotFound: spam 1 does not exist
        '''
        lines = cls._build_lines(body)
        if lines and lines[0].startswith('#'):
            raise errors.parse(lines[0])
        return cls._decode(lines)

    @classmethod
    def _query(cls, body):
        '''Return a tuple list representing id, name of matching resourses
        >>> body = """
        ...
        ... 1: spam
        ... 2: ham
        ... 3: eggs"""
        >>> RTResponse._query(body)
        [('1', 'spam'), ('2', 'ham'), ('3', 'eggs')]
        >>> body = 'No matching results.'
        >>> RTResponse._query(body)
        []
        '''
        lines = cls._build_lines(body)
        if errors.NO_MATCHING.match(lines[0]):
            return []
        return [(k, v) for k,v in cls._decode(lines).iteritems()]

    @classmethod
    def _detailed_query(cls, body):
        '''Return a list of ordered dictionary representing matching resourses
        >>> body = """
        ... spam: 1
        ... ham: 2
        ... --
        ... spam: 4
        ... ham: 5"""
        >>> RTResponse._detailed_query(body)
        [OrderedDict([('spam', '1'), ('ham', '2')]), OrderedDict([('spam', '4'), ('ham', '5')])]
        >>> body = 'No matching results.'
        >>> RTResponse._detailed_query(body)
        []
        '''
        lines = [cls._build_lines(b) for b in body.split('--')]
        if errors.NO_MATCHING.match(lines[0][0]):
            return []
        return [cls._decode(line) for line in lines]

    @staticmethod
    def _decode(lines):
        '''Decode valid key-value listed response
        >>> RTResponse._decode(['spam: 1','ham: 2,3', 'eggs:'])
        OrderedDict([('spam', '1'), ('ham', '2,3'), ('eggs', '')])
        '''
        ret = OrderedDict()
        for line in lines:
            k,v = line.split(':', 1)
            ret[k] = v.lstrip(' ')
        return ret

    @classmethod
    def _build_lines(cls, body):
        '''Build logical lines as RFC822
        >>> body = """
        ...
        ... spam: 1
        ... ham: 2,
        ...     3
        ... egg:"""
        >>> RTResponse._build_lines(body)
        ['spam: 1', 'ham: 2,3', 'egg:']
        '''
        logic_lines = []
        for line in body.splitlines():
            if not len(line):
                continue
            elif line[0].isspace():
               logic_lines[-1] += line.lstrip(' ')
            else:
               logic_lines.append(line)
        return logic_lines