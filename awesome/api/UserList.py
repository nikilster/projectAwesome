from data.DataApi import DataApi

from User import User

from ..util.Logger import Logger

class UserList:
    '''For getting and serializing list of users'''

    class Options:
        USER_FOLLOW = 0      # need to pass in 'user' parameter also

    #
    # Static methods to get vision lists
    #
    @staticmethod
    def getByUserIds(userIds):
        models = DataApi.getUsersFromIds(userIds)
        return UserList(models)


    #
    # Utility methods
    #
    def users(self):
        '''Get list of users'''
        return [User(model) for model in self._models]


    def toDictionary(self, options=[], user=None):
        '''To dictionary'''

        # Remeber not to use 'user' because it is a parameter
        idToUser = dict([(u.id(), u) for u in self.users()])

        # If we need to, fetch Follows to check if there are return follows
        # for if people in userIds follow the user passed in as a parameter
        if user and UserList.Options.USER_FOLLOW in options:
            userFollows = DataApi.getUserFollowsFromList(user.model(),
                                                         idToUser.keys())
            userFollowIds = [f.userId for f in userFollows]
            from Follow import Follow
            idToFollow = dict([(f.userId, Follow(f)) for f in userFollows])

        objList = []
        for u in self.users():
            obj = u.toDictionary()

            if user and UserList.Options.USER_FOLLOW in options:
                if u.id() in idToFollow:
                    follow = idToFollow[u.id()]
                    obj[User.Key.BLESSED] = follow.blessed(user)
                    obj[User.Key.FOLLOW] = True
                else:
                    obj[User.Key.BLESSED] = False
                    obj[User.Key.FOLLOW] = False
            objList.append(obj)
        return objList

    #
    # Private
    #
    def __init__(self, models):
        '''Private: do not use.'''
        self._models = models

# $eof
