###############################################################################
# VisionList
#
# This is used for getting different types of vision lists, and getting
# information across all the visions. This class will commonly be used for
# querying visions in different ways, for transmission to the front-end.
#
# *** IMPORTANT NOTE ***
#   - All methods on visions which affect the user's vision list order should
#     NOT be here. This is because currently the Vision and VisionList
#     classes do not know anything about a user's vision list order.
#
#   - Check out the User object to create, add, move, repost visions!!!!!!!
#   - ONLY use this for getting lists of visions (w/o need for user vision
#     list order)
#
###############################################################################

from data.DataApi import DataApi

from Vision import Vision

from ..util.Logger import Logger

class VisionList:
    #
    # Static methods to get vision lists
    #

    # Gets vision list for main page. This is the most recently created public
    # visions.
    @staticmethod
    def getMainPageVisions():
        models = DataApi.getMainPageVisions()
        return VisionList(models)

    # Gets vision of a the 'targetUser' based upon the privileges of 'user'.
    # If 'user' == None, treat public lookup of user visions.
    @staticmethod
    def getUserVisions(user, targetUser):
        # user is allowed to be None, but not target user
        assert targetUser, "Invalid target user"
        userId = None
        if user:
            userId = user.id()
        models = DataApi.getVisionsForUser(userId, targetUser.id())
        return VisionList(models)

    @staticmethod
    def getWithVision(vision):
        assert vision, "Invalid vision"
        return VisionList([vision._getModel()])

    #
    # Getters
    #
    def visions(self):
        return [Vision(model) for model in self._visionModels]

    def toDictionaryDeep(self):
        visions = self._visionModels
        visionList = []

        pictureIds = set([vision.pictureId for vision in visions])
        pictureIds.discard(0)
        pictures = DataApi.getPicturesFromIds(pictureIds)
        idToPicture = dict([(picture.id, picture) for picture in pictures])
        idToPicture[0] = ""

        userIds = set([vision.userId for vision in visions])
        users = DataApi.getUsersFromIds(userIds)
        idToUser = dict([(user.id, user) for user in users])

        visionIds = [vision.id for vision in visions]
        comments = DataApi.getVisionCommentsFromVisionIds(visionIds)
        idToComments = {}
        for comment in comments:
            if not comment.visionId in idToComments.keys():
                idToComments[comment.visionId] = [comment]
            else:
                idToComments[comment.visionId].append(comment)

        authorIds = set([comment.authorId for comment in comments])
        authors = DataApi.getUsersFromIds(authorIds)
        idToAuthor = dict([(user.id, user) for user in authors])

        for vision in visions:
            obj = vision.toDictionary()
            obj['name'] = idToUser[vision.userId].fullName
            if vision.pictureId != 0:
                obj['picture'] = idToPicture[vision.pictureId].toDictionary()
            obj['comments'] = []
            if vision.id in idToComments.keys():
                for comment in idToComments[vision.id]:
                    commentObj = comment.toDictionary()
                    author = idToAuthor[comment.authorId]
                    commentObj['name'] = author.fullName
                    commentObj['picture'] = author.picture
                    obj['comments'].append(commentObj)
            visionList.append(obj)
        return visionList

    def __init__(self, visionModels):
        self._visionModels = visionModels

# $eof
