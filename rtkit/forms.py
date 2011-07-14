from restkit.forms import BoundaryItem, MultipartForm

class RTBoundaryItem(BoundaryItem):
    def encode_unreadable_value(self, value):
        if self.name == 'content':
            return _content_encode(value)
        else:
            return super(RTBoundaryItem, self).encode_unreadable_value(value)

def encode(value, boundary, headers):
    if len(value) == 1 and 'content' in value:
        value = 'content={0}'.format(_content_encode(value['content']))
        headers.setdefault('Content-Type',
                        'application/x-www-form-urlencoded; charset=utf-8')
    else:
        value = MultipartForm(value, boundary, headers, RTBoundaryItem)
    return value

def _content_encode(value):
    return '\n'.join(['{0}: {1}'.format(k,v) for k,v in value.iteritems()])
