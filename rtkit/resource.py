import re
from restkit import Resource, Response
import errors

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
        >>> payload = {'a': 1, 'b':2, 'c':3, }
        >>> RTResource.encode(payload)
        u'content=a: 1\nc: 3\nb: 2\n'
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

    def single(self):
        lines = self.build_lines(self.body_string())
        if lines and lines[0].startswith('#'):
            raise errors.parse(lines[0])
        return self.decode(lines)

    @staticmethod
    def decode(lines):
        '''Decode valid key-value listed response
        >>> d = RTResponse.decode(['spam: 1','ham: 2,3', 'eggs:'])
        >>> d == {'spam': '1', 'ham': '2,3', 'eggs': ''}
        True
        '''
        ret = {}
        for line in lines:
            k,v = line.split(':', 1)
            ret[k] = v.lstrip(' ')
        return ret

    @classmethod
    def build_lines(cls, body):
        '''Build logical lines as RFC822
        >>> body = """
        ...
        ... spam: 1
        ... ham: 2,
        ...     3
        ... egg:"""
        >>> RTResponse.build_lines(body)
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