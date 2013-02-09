import os
import re

__all__ = ['User', 'Queue', 'Ticket', 'Attachment', 'History', 'Links']

if os.environ.get('__GEN_DOCS__', None):
    __all__.insert(0, "RTEntity")


class RTEntity(object):
    """Base Class for an Entity"""
    def __init__(self, id, tracker):
        self._id = id
        self.tracker = tracker

    @property
    def id(self):
        """:return: int with the ID"""
        return int(self._id.split('/')[1])

    @staticmethod
    def api():
        """:return: NotImplementedError - needs to be implemented in subclass"""
        raise NotImplementedError


class User(RTEntity):
    """User Object"""
    def __init__(self, id, tracker, **kwargs):
        super(User, self).__init__(id, tracker)
        self.name = kwargs.get('Name')
        self.mail = kwargs.get('EmailAddress')
        self.realname = kwargs.get('RealName')
        self.language = kwargs.get('Lang')

    def __str__(self):
        return '{s.realname} <{s.mail}>'.format(s=self)

    @staticmethod
    def api():
        """:return: str with 'user'"""
        return 'user'


class Queue(RTEntity):
    """Queue Object"""
    def __init__(self, id, tracker, **kwargs):
        super(Queue, self).__init__(id, tracker)

        self.name = kwargs.get('Name')
        """Queue Name"""

        self.description = kwargs.get('Description')
        """Queue Description"""

    def __str__(self):
        return '{s.id}: {s.name}'.format(s=self)

    def search_tickets(self, query="", active=True, order='id', ):
        final_query = "Queue = '%s'" % (self.name, )
        if query:
            final_query = "%s and %s" % (final_query, query, )
        if active:
            final_query = "%s and (Status = 'new' or Status = 'open' or Status = 'stalled')" % (final_query, )
        return self.tracker.search_tickets(query=final_query, order=order)

    @staticmethod
    def api():
        """:return: str with 'queue'"""
        return 'queue'

cf_matcher = re.compile("^CF.\{(?P<name>[^}]*)\}$")


class Ticket(RTEntity):
    """Ticket Object"""
    def __init__(self, id, tracker, **kwargs):
        super(Ticket, self).__init__(id, tracker)

        self.subject = kwargs.get('Subject')
        """Subject"""

        self._queue_name = kwargs.get('Queue')
        """Queue"""

        self.owner = kwargs.get('Owner')
        """Owner"""

        self.requestors = kwargs.get('Requestors')
        """Requestors"""

        self.creator = kwargs.get('Creator')
        """Creator"""

        self.status = kwargs.get('Status')
        """Status"""

        self.priority = kwargs.get('Priority')
        """Priority"""

        self.delta = {
            'worked': kwargs.get('TimeWorked'),
            'estimated': kwargs.get('TimeEstimated'),
            'left': kwargs.get('TimeLeft'),
        }
        """Time Deltas dictionary with keys

           * worked
           * estimated
           * left
        """

        self.date = {
            'created': kwargs.get('Created'),
            'started': kwargs.get('Started'),
            'due': kwargs.get('Due'),
            'resolved': kwargs.get('Resolved'),
            'updated': kwargs.get('LastUpdated'),
        }
        """Dates as dicionary with keys

           * created
           * started
           * due
           * resolved
           * updated
        """

        self.cf = {}
        for k, v in kwargs.items():
            matcher = cf_matcher.match(k)
            if matcher:
                self.cf[matcher.group('name')] = v

    def __str__(self):
        return '{s.id}: {s.subject}'.format(s=self)

    @staticmethod
    def api():
        """:return: str with 'ticket'"""
        return 'ticket'


class Attachment(RTEntity):
    """Attachment Object
    """
    def __init__(self, id, tracker, **kwargs):
        super(Attachment, self).__init__(id, tracker)

        self.filename = kwargs.get('Filename')
        """Filename"""

        self.ctype = kwargs.get('ContentType')
        """ContentType"""

        self.encoding = kwargs.get('ContentEncoding')
        """ContentEncoding"""

        self.content = kwargs.get('Content')
        """Content"""

    def __str__(self):
        return '[{s.ticket}]{s.id}'.format(s=self)

    @property
    def id(self):
        return int(self._id)

    @staticmethod
    def api():
        """:return: str with 'attachments'"""
        return 'attachments'


class History(RTEntity):
    """History Object

    .. todo:: `History` not implemented
    """
    pass


class Links(RTEntity):
    """Links Object

    .. todo:: `Links` not implemented
    """
    pass
