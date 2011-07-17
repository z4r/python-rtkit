from restkit.filters import BasicAuth
from rtkit.resource import RTResource
from entities import *

class Tracker(RTResource):
    def __init__(self, uri, username, password, language='en'):
        auth = BasicAuth(username,password)
        super(Tracker, self).__init__(uri, filters=[auth,])
        self.user = self.get_user(username)
        self.language = self.user.language or language

    def get_user(self, value):
        return self._get_entity(User, value)

    def get_queue(self, value):
        return self._get_entity(Queue, value)

    def get_ticket(self, value):
        return self._get_entity(Ticket, value)

    def _get_entity(self, Entity, value):
        r = self.get(path='{0}/{1}'.format(Entity.api(), value))
        return Entity(**dict(r.parsed[0]))


