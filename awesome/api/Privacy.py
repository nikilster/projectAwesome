
class UserPrivacy:
    '''Enum for user privacy policies'''
    PRIVATE = 0
    PUBLIC = 1
    INVALID = 2

class VisionPrivacy:
    '''Enum for vision privacy policies'''
    PRIVATE = 0
    PUBLIC = 1
    INVALID = 2

class Relationship:
    '''Define and get relationship between users'''
    NONE = 0    # either anonymous user, or there is no relationship
    SELF = 1    # user and target user are same person
    SHARED = 2  # target user has shared with user requesting data

    @staticmethod
    def get(userId, targetUserId):
        assert targetUserId != None and targetUserId > 0, \
            "Invalid target user id: %s" % (str(targetUserId))
        assert userId == None or userId > 0, \
               "Invalid user id: %s" % (str(userId))

        # Right now we don't support the mastermind group so you either are your
        # self, or you aren't related.
        if None != userId and userId == targetUserId:
            return Relationship.SELF
        return Relationship.NONE

# $eof
