from data.DataApi import DataApi

from ..util.Verifier import Verifier
from ..util.PasswordEncrypt import PasswordEncrypt
from ..util.Logger import Logger

#TODO: Why does (the ..) this work?
from ..Constant import Constant

from VisionComment import VisionComment

from FlashMessages import *
from S3Util import ImageFilePreview, ImageUrlUpload, S3Vision, ProfilePicture


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

    # Used for packaging into JSON
    def toDictionary(self):
        return {'id' : self.id(),
                'userId' : self.userId(),
                'text' : self.text(),
                'parentId' : self.parentId(),
                'rootId' : self.rootId(),
               }

    # Get comments for this vision with privileges of 'user'.
    # If 'user' == None, then act as if public is viewing comments
    def getComments(self, user):
        userId = None
        if user:
            userId = user.id()
        comments = DataApi.getVisionComments(self.id(), userId)

        objs = []
        Logger.debug("COMMENTS: " + str(comments))
        if comments and len(comments) > 0:
            authorIds = set([comment.authorId for comment in comments])
            authors = DataApi.getUsersFromIds(authorIds)
            idToAuthor = dict([(user.id, user) for user in authors])

            for comment in comments:
                obj = comment.toDictionary()
                obj['name'] = idToAuthor[comment.authorId].fullName
                obj['picture'] = idToAuthor[comment.authorId].picture
                objs.append(obj)
        return objs

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
