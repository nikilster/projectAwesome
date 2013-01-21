from data.DataApi import DataApi

from ..util.Logger import Logger

class Follow:
    '''For fetching and setting follows'''
    #
    # Static methods
    #

    @staticmethod
    def get(follower, user):
        '''Get Follow, or None'''
        model = DataApi.getFollow(follower.model(), user.model())
        if model == DataApi.NO_OBJECT_EXISTS:
            return None
        return Follow(model)

    @staticmethod
    def getUserFollowCount(user):
        '''Get number of people this user follows'''
        return DataApi.getUserFollowCount(user.model())

    @staticmethod
    def getUserFollowerCount(user):
        '''Get number of people following this user'''
        return DataApi.getUserFollowerCount(user.model())

    @staticmethod
    def getCount():
        '''Gets count of follows'''
        return DataApi.getFollowCount()


    #
    # Getters
    #
    def id(self):
        return self._model.id
    def followerId(self):
        '''User doing the following'''
        return self._model.followerId
    def userId(self):
        '''User being followed'''
        return self._model.userId
    def blessed(self, user):
        '''True if this Follow is blessed by the user being followed.

        This means that the follower can see the users private data.
        
        'user' parameter is the user inquiring if this connection is blessed.
               This user must be either the follower or the followee of this
               connection to read whether this link is blessed. This is here
               to maintain privacy on the site so that it is impossible to
               accidentally let out knowledge of a blessed follow.

        NOTE: if you MUST know if the connection is blessed (as in you are
              the admin dashboard, emailer, or something else, use a private
              method such as self._ADMIN_blessed()
        '''
        if user != None and \
           (user.id() == self.followerId() or \
            user.id() == self.userId()):
            return self._model.blessed
        else:
            return False

    #
    # Private methods: Don't use these externally
    #
    def __init__(self, model):
        assert model != None, "Invalid model for follow"
        self._model = model

    def _ADMIN_blessed(self):
        return self._model.blessed

# eof
