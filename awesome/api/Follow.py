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
    def getUserFollows(user, number=0):
        '''Get list of Follow objects of people this this user follows'''
        models = DataApi.getUserFollows(user.model(), number)
        return [Follow(model) for model in models]

    @staticmethod
    def getUserFollowers(user, number=0):
        '''Get list of Follow objects of people following this user'''
        models = DataApi.getUserFollowers(user.model(), number)
        return [Follow(model) for model in models]


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
    def blessed(self):
        '''True if the follower can view the user's private data'''
        return self._model.blessed

    #
    # Private methods: Don't use these externally
    #
    def __init__(self, model):
        assert model != None, "Invalid model for follow"
        self._model = model

# eof
