###############################################################################
# Vision
#
# This is the Vision abstraction that should be used for getting vision
# properties about visions.
#
# *** IMPORTANT NOTE ***
#   - All methods on visions which affect the user's vision list order should
#     NOT be here. This is because currently the Vision and VisionList
#     classes do not know anything about a user's vision list order.
#
#   - Check out the User object to create, add, move, repost visions!!!!!!!
#
###############################################################################
from data.DataApi import DataApi

from VisionCommentList import VisionCommentList
from Picture import Picture

from ..util.Logger import Logger

class Vision:
    #
    # Static methods to get a vision
    #
    @staticmethod
    def getById(visionId):
        model = DataApi.getVision(visionId)
        if DataApi.NO_OBJECT_EXISTS == model:
            return None
        return Vision(model)

    # This is used internally within API when necessary. Try not to use this.
    @staticmethod
    def _getByModel(model):
        return Vision(model)

    #
    # Getter methods
    #
    def id(self):
        return self._model.id
    def userId(self):
        return self._model.userId
    def text(self):
        return self._model.text
    def pictureId(self):
        return self._model.pictureId
    # This is the parent vision id.
    # Returns 0 if vision is original (not reposted).
    def parentId(self):
        return self._model.parentId
    # All visions are part of a vision tree based upon re-posting. This
    # indicates the root vision id of the tree with vision belongs to.
    def rootId(self):
        return self._model.rootId
    def removed(self):
        return self._model.removed
    def privacy(self):
        return self._model.privacy

    #
    # Convenience methods
    #
    def isOriginalVision(self):
        return 0 == self.parentId()
    def isRootVision(self):
        return self.id() == self.rootId()

    #
    # Convenience methods that access DB again
    #

    # returns Picture object for this Vision, or None
    def picture(self):
        return Picture.getById(self.pictureId())

    # returns User object that owns this vision, or None
    def user(self):
        # import here to avoid circular imports
        from User import User
        return User.getById(self.userId())

    # Used for packaging into JSON
    def toDictionary(self):
        return {'id' : self.id(),
                'userId' : self.userId(),
                'text' : self.text(),
                'parentId' : self.parentId(),
                'rootId' : self.rootId(),
               }

    # If accessing many visions, use VisionList instead! It can batch up
    # DB queries across visions for better performance
    def toDictionaryDeep(self):
        obj = self.toDictionary()
        picture = self.picture()
        if picture:
            obj['picture'] = picture.toDictionary()
        return obj

    # Get comments for this vision with privileges of 'user'.
    # If 'user' == None, then act as if public is viewing comments
    def getComments(self, user):
        userId = None
        if user:
            userId = user.id()
        comments = DataApi.getVisionComments(self.id(), userId)
        commentList = VisionCommentList.getEmptyList()
        if comments:
            commentList = VisionCommentList._getWithModels(comments)
        return commentList


    #
    # Private methods
    #
    def __init__(self, model):
        assert model, "Invalid vision model"
        self._model = model

    # try not to used, but used rarely now
    def _getModel(self):
        return self._model

# $eof
