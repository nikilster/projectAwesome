from data.DataApi import DataApi

from Follow import Follow

from ..util.Logger import Logger

class FollowList:
    '''For getting and serializing follow lists
   
    This class if mainly used for the toDictionary function which creates the
    objects for follow and follower user lists
    '''

    class Options:
        '''For toDictionary'''
        FOLLOW_LIST = 1     # Output as a user follow list
        FOLLOWER_LIST = 2   # Output as a user follower list

        USER_FOLLOW = 3     # To see if user list 
                            # - only used with FOLLOW_LIST option

    #
    # Static methods to get vision lists
    #

    @staticmethod
    def getUserFollows(user, number=0):
        '''Get list of Follow objects of people this this user follows'''
        models = DataApi.getUserFollows(user.model(), number)
        return FollowList(models)

    @staticmethod
    def getUserFollowers(user, number=0):
        '''Get list of Follow objects of people following this user'''
        models = DataApi.getUserFollowers(user.model(), number)
        return FollowList(models)

    #
    # Getters
    #
    def followList(self):
        '''Returns array of Follow objects in this list'''
        return [Follow(model) for model in self._models]

    #
    # Utility methods
    #
    def length(self):
        return len(self.followList())

    def toDictionary(self, options=[], user=None):
        '''To dictionary'''
        from User import User
        # get list of user ids we want to fetch
        if FollowList.Options.FOLLOW_LIST in options:
            userIds = [follow.userId() for follow in self.followList()]
        elif FollowList.Options.FOLLOWER_LIST in options:
            userIds = [follow.followerId() for follow in self.followList()]
        else:
            assert False, "Should have FOLLOW_LIST or FOLLOWER_LIST options"

        users = User.getByUserIds(userIds)
        # don't user 'user' because it is a parameter
        idToUser = dict([(u.id(), u) for u in users])

        # If we need to, fetch Follows to check if there are return follows
        # for if people in userIds follow the user passed in as a parameter
        if FollowList.Options.USER_FOLLOW in options:
            userFollows = DataApi.getUserFollowsFromList(user.model(),
                                                           userIds)
            userFollowIds = [f.userId for f in userFollows]

        objList = []
        for follow in self.followList():
            if FollowList.Options.FOLLOW_LIST in options:
                u = idToUser[follow.userId()]
            elif FollowList.Options.FOLLOWER_LIST in options:
                u = idToUser[follow.followerId()]
            else:
                assert False, "Should have FOLLOW_LIST or FOLLOWER_LIST options"
            obj = u.toDictionary()

            obj[User.Key.BLESSED] = follow.blessed(user)

            if FollowList.Options.USER_FOLLOW in options:
                obj[User.Key.FOLLOW] = u.id() in userFollowIds

            objList.append(obj)
        return objList

    #
    # Private
    #
    def __init__(self, models):
        '''Private: do not use.'''
        self._models = models

# $eof
