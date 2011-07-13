import mimetypes
import os
from restkit.forms import MultipartForm, BoundaryItem
from restkit.util import url_quote, to_bytestring

class RTBoundaryItem(BoundaryItem):
    def __init__(self, name, value, fname=None, filetype=None, filesize=None):
        self.name = url_quote(name)
        if value is not None and not hasattr(value, 'read'):
            if name == 'content':
                pstr = ['{0}: {1}'.format(k,v) for k,v in value.iteritems()]
                value = u'{0}'.format('\n'.join(pstr))
            else:
                value = url_quote(value, safe=safe)
            self.size = len(value)
        self.value = value
        if fname is not None:
            if isinstance(fname, unicode):
                fname = fname.encode("utf-8").encode("string_escape").replace('"', '\\"')
            else:
                fname = fname.encode("string_escape").replace('"', '\\"')
        self.fname = fname
        if filetype is not None:
            filetype = to_bytestring(filetype)
        self.filetype = filetype

        if isinstance(value, file) and filesize is None:
            try:
                value.flush()
            except IOError:
                pass
            self.size = int(os.fstat(value.fileno())[6])


class RTMultipartForm(MultipartForm):
    def __init__(self, params, boundary, headers):
        self.boundary = boundary
        self.boundaries = []
        self.size = 0

        self.content_length = headers.get('Content-Length')

        if hasattr(params, 'items'):
            params = params.items()

        for param in params:
            name, value = param
            if hasattr(value, "read"):
                fname = getattr(value, 'name')
                if fname is not None:
                    filetype = ';'.join(filter(None, mimetypes.guess_type(fname)))
                else:
                    filetype = None
                if not isinstance(value, file) and self.content_length is None:
                    value = value.read()

                boundary = BoundaryItem(name, value, fname, filetype)
            else:
                boundary = RTBoundaryItem(name, value)
            self.boundaries.append(boundary)

    def get_size(self):
        if self.content_length is not None:
            return int(self.content_length)
        size = 0
        for boundary in self.boundaries:
            size = size + boundary.size + len(boundary.encode_hdr(self.boundary)) + len('\r\n')
        return size + len("--%s--\r\n" % self.boundary)