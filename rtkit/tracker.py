from rtkit.resource import RTResource
from entities import *

class Tracker(RTResource):
    def __init__(self, url, username, password, auth, language='en'):
        super(Tracker, self).__init__(url, username, password, auth)
        self.user = self.get_user(auth.username)
        self.language = self.user.language or language

    def get_user(self, value):
        return self._get_entity(User, value)

    def get_queue(self, value):
        return self._get_entity(Queue, value)

    def get_ticket(self, value):
        return self._get_entity(Ticket, value)

    def search_tickets(self, query, order):
        raise NotImplementedError

    def create_ticket(self, content, attachments=None):
        raise NotImplementedError

    def comment_ticket(self, content, attachments=None):
        raise NotImplementedError

    def get_attachment(self, ticket_id, value):
        return self._get_subentity(Ticket, ticket_id, Attachment, value)

    def get_history(self, ticket_id, value=None, format='l'):
        return self._get_subentity(Ticket, ticket_id, History, value, format)

    def get_links(self, ticket_id):
        return self._get_subentity(Ticket, ticket_id, Links)

    def change_links(self, ticket_id, content):
        raise NotImplementedError

    def _get_entity(self, Entity, value):
        r = self.get(path='{0}/{1}'.format(Entity.api(), value))
        return Entity(**dict(r.parsed[0]))

    def _get_subentity(self, Entity, e_value, SubEntity, s_value, format=None):
        path = '{0}/{1}/{2}/{3}'.format(Entity.api(), e_value, SubEntity.api(), s_value)
        if format:
            path += '?{0}'.format(format)
        r = self.get(path=path)
        return SubEntity(**dict(r.parsed[0]))




