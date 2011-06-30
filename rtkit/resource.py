from rtkit import __version__
from restkit import Resource, ClientResponse

USER_AGENT = 'pyRTkit/{0}'.format(__version__)
HEADER_PATTERN = 'RT/(?P<version>\d+\.\d+\.\d+)\s+(?P<status>(?P<status_int>\d+)\s+\w+)'


class RTResource(Resource):
    def __init__(self, uri, **kvargs):
        kvargs['response_class'] = RTResponse
        super(RTResource, self).__init__(uri, **kvargs)

    def request(self, method, path=None, payload=None, headers=None, **kvargs):
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
            **kvargs
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

class RTResponse(ClientResponse):#TODO
    pass