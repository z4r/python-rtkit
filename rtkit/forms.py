from restkit.forms import BoundaryItem

class RTBoundaryItem(BoundaryItem):
    def encode_unreadable_value(self, value):
        if self.name == 'content':
            return single_encode(value)
        else:
            return super(RTBoundaryItem, self).encode_unreadable_value(value)

def single_encode(value):
    pstr = ['{0}: {1}'.format(k,v) for k,v in value.iteritems()]
    return u'{0}'.format('\n'.join(pstr))