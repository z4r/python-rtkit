from restkit.filters import BasicAuth
from resource import RTResource
from entity import User

class Tracker(RTResource):
    def __init__(self, uri, username, password, language, logger):
        self.logger = logger
        auth = BasicAuth(username,password)
        super(Tracker, self).__init__(uri, filters=[auth,])
        self.user = self.get_user(username)
        self.logger.info('Logged As: {0}'.format(self.user))
        self.language = self.user.language or language
        self.logger.info('Tracker language: {0}'.format(self.language))

    def get_user(self, user):
        init_user = self._get_entity('user', user)
        return User(**dict(init_user))

    def _get_entity(self, type, id):
        r = self.get(path='{0}/{1}'.format(type, id))
        return r.parsed[0]


