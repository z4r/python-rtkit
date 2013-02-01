
__all__ = ['User', 'Queue', 'Ticket', 'Attachment', 'History', 'Links']


class RTEntity(object):
    """Base Object"""
     
    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return int(self._id.split('/')[1])

    @staticmethod
    def api():
        """returns the objects api"""
        raise NotImplementedError


class User(RTEntity):
    """User Object"""
     
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
    """Queue Object"""
    def __init__(self, id, **kwargs):
        super(Queue, self).__init__(id)
        
        self.name = kwargs.get('Name')
        """Queue Name"""
        
        self.description = kwargs.get('Description')
        """Queue Description"""
        
    def __str__(self):
        return '{s.id}: {s.name}'.format(s=self)

    @staticmethod
    def api():
        return 'queue'


class Ticket(RTEntity):
    """Ticket Object"""
    def __init__(self, id, **kwargs):
        super(Ticket, self).__init__(id)
        
        
        self.subject = kwargs.get('Subject')
        """Subject"""
        
        self._queue_name = kwargs.get('Queue')
        """Queue"""
        
        self.owner = kwargs.get('Owner')
        """Owner"""
        
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
        
    def __str__(self):
        return '{s.id}: {s.subject}'.format(s=self)

    @staticmethod
    def api():
        return 'ticket'


class Attachment(RTEntity):
    """Attachment Object
    """
    def __init__(self, id, **kwargs):
        super(Attachment, self).__init__(id)
        
       
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
