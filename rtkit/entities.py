class RTEntity(object):
    pass


class User(RTEntity):
    def __init__(self, id, **kwargs):
        self._id = id
        self.name = kwargs.get('Name')
        self.mail = kwargs.get('EmailAddress')
        self.rname = kwargs.get('RealName')
        self.language = kwargs.get('Lang')

    @property
    def id(self):
        return self._id.split('/')[1]

    def __str__(self):
        return '{s.id}: {s.rname} <{s.mail}>'.format(s=self)