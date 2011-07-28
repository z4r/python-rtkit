__all__ = ['User', 'Queue', 'Ticket', 'Attachment', 'History', 'Links']

class RTEntity(object):
    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return int(self._id.split('/')[1])

    @staticmethod
    def api():
        raise NotImplementedError


class User(RTEntity):
    def __init__(self, id, **kwargs):
        super(User, self).__init__(id)
        self.name = kwargs.get('Name')
        self.mail = kwargs.get('EmailAddress')
        self.realname = kwargs.get('RealName')
        self.language = kwargs.get('Lang')

    def __str__(self):
        return '{s.realname} <{s.mail}>'.format(s=self)

    @staticmethod
    def api():
        return 'user'


class Queue(RTEntity):
    def __init__(self, id, **kwargs):
        super(Queue, self).__init__(id)
        self.name = kwargs.get('Name')
        self.description = kwargs.get('Description')

    def __str__(self):
        return '{s.id}: {s.name}'.format(s=self)

    @staticmethod
    def api():
        return 'queue'


class Ticket(RTEntity):
    def __init__(self, id, **kwargs):
        super(Ticket, self).__init__(id)
        self.subject = kwargs.get('Subject')
        self._queue_name = kwargs.get('Queue')
        self.owner = kwargs.get('Owner')
        self.creator = kwargs.get('Creator')
        self.status = kwargs.get('Status')
        self.priority = kwargs.get('Priority')
        self.delta = {
            'worked' : kwargs.get('TimeWorked'),
            'estimated' : kwargs.get('TimeEstimated'),
            'left' : kwargs.get('TimeLeft'),
        }
        self.date = {
            'created' : kwargs.get('Created'),
            'started' : kwargs.get('Started'),
            'due' : kwargs.get('Due'),
            'resolved' : kwargs.get('Resolved'),
            'updated' : kwargs.get('LastUpdated'),
        }

    def __str__(self):
        return '{s.id}: {s.subject}'.format(s=self)

    @staticmethod
    def api():
        return 'ticket'

class Attachment(RTEntity):
    def __init__(self, id, **kwargs):
        super(Attachment, self).__init__(id)
        self.filename = kwargs.get('Filename')
        self.ctype = kwargs.get('ContentType')
        self.encoding = kwargs.get('ContentEncoding')
        self.content = kwargs.get('Content')

    def __str__(self):
        return '[{s.ticket}]{s.id}'.format(s=self)

    @property
    def id(self):
        return int(self._id)

    @staticmethod
    def api():
        return 'attachments'


class History(RTEntity):
    pass


class Links(RTEntity):
    pass
