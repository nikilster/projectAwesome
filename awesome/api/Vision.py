from data.DataApi import DataApi

from VisionCommentList import VisionCommentList
from Picture import Picture

from ..util.Logger import Logger

class Vision:
    '''For fetching and getting properties on visions.

    *** IMPORTANT NOTE ***
    All methods on visions which affect the user's vision list order should
    NOT be here. This is because currently the Vision and VisionList
    classes do not know anything about a user's vision list order.

    Check out the User object to create, add, move, repost visions!!!!!!!
    '''

    #
    # Static methods to get a vision
    #

    @staticmethod
    def getById(visionId):
        '''Get vision by id, else None'''
        model = DataApi.getVision(visionId)
        if DataApi.NO_OBJECT_EXISTS == model:
            return None
        return Vision(model)

    @staticmethod
    def _getByModel(model):
        '''*** DON'T USE THIS: used internally within API for now ***'''
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
    def parentId(self):
        '''Returns 0 if vision is original, and parent vision id if reposted'''
        return self._model.parentId
    def rootId(self):
        '''Returns vision id of root vision in the vision repost tree'''
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

    def picture(self):
        '''Returns Picture object for this Vision, or None'''
        return Picture.getById(self.pictureId())

    def user(self):
        '''Returns User object that owns this vision, or None'''
        # import here to avoid circular imports
        from User import User
        return User.getById(self.userId())

    def toDictionary(self):
        '''Used for packaging into JSON'''
        return {'id' : self.id(),
                'userId' : self.userId(),
                'text' : self.text(),
                'parentId' : self.parentId(),
                'rootId' : self.rootId(),
               }

    def toDictionaryDeep(self):
        '''Used for packaging into JSON

        If accessing many visions, use VisionList instead! It can batch up
        DB queries across visions for better performance
        '''
        obj = self.toDictionary()
        picture = self.picture()
        if picture:
            obj['picture'] = picture.toDictionary()
        return obj

    def getComments(self, user):
        '''Get comments for this vision with privileges of 'user'.

        If 'user' == None, then act as if public is viewing comments
        '''
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

    def _getModel(self):
        '''Try not to use, but used internally in API a little'''
        return self._model

# $eof
