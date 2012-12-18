from data.DataApi import DataApi

from VisionComment import VisionComment
from VisionCommentList import VisionCommentList
from Picture import Picture
from Privacy import Relationship, VisionPrivacy

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
    # Constants, enums
    #
    class Key:
        ''' For dictionary use'''
        ID = 'id'
        USER_ID = 'userId'
        TEXT = 'text'
        PARENT_ID = 'parentId'
        ROOT_ID = 'rootId'
        PRIVACY = 'privacy'
        # These two aren't always filled 
        PICTURE = 'picture'
        NAME = 'name'
        COMMENTS = 'comments'

    #
    # Static methods to get a vision
    #

    @staticmethod
    def getById(visionId, inquiringUser):
        '''Get vision by id with privileges of inquiringUser, else None.
       
        If inquiringUser==None, assume public is trying to access this vision.
        '''
        model = DataApi.getVision(visionId)
        if DataApi.NO_OBJECT_EXISTS == model:
            return None
        vision = Vision(model)

        # Ensure that user can access this vision
        relationship = Relationship.get(
                            inquiringUser.id() if inquiringUser else None,
                            vision.userId())
        ok = False
        if Relationship.NONE == relationship:
            # if no relationship, vision must be public
            if VisionPrivacy.PUBLIC == vision.privacy():
                ok = True
        elif Relationship.SELF == relationship:
            # if it is your own vision, you def have access
            ok = True

        if True == ok:
            return vision
        else:
            return None

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
    def model(self):
        ''' Get internal DB model'''
        return self._model

    #
    # Convenience methods
    #
    def isOriginalVision(self):
        return 0 == self.parentId()
    def isRootVision(self):
        return self.id() == self.rootId()
    def isPublic(self):
        return self.privacy() == VisionPrivacy.PUBLIC
    
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

    def comments(self, maxComments):
        '''Get recent comments for this vision with privileges of 'user'.

        If 'user' == None, then act as if public is viewing comments.
        maxComments should be > 0 and < 1000.
        '''
        return VisionCommentList.getFromVision(self, maxComments)


    def edit(self, text, isPublic):
        '''Set new text and/or privacy value'''

        # Make sure text is valid
        text = text.strip()
        if len(text) < 0 or len(text) > 200:
            return False

        # Make sure to maintain privacy! If already private, can't change to
        # public!
        if False == self.isPublic() and \
           True == isPublic and \
           DataApi.visionHasComments(self.id()):
            return False
        # ok, now we can make the change
        privacy = VisionPrivacy.SHAREABLE
        if isPublic:
            privacy = VisionPrivacy.PUBLIC
        return DataApi.editVision(self.id(), text, privacy)

    def addComment(self, user, text):
        '''Return new comment, or None.
        
        Note: Assumes vision is already vetted to be written by user.'''
        if len(text.strip()) > 0:
            commentModel = DataApi.addVisionComment(self.model(),
                                                    user.model(),
                                                    text)
            if DataApi.NO_OBJECT_EXISTS == commentModel:
                return None
            else:
                return VisionComment._getByModel(commentModel)
        return None

    def toDictionary(self):
        '''Used for packaging into JSON'''
        return {Vision.Key.ID           : self.id(),
                Vision.Key.USER_ID      : self.userId(),
                Vision.Key.TEXT         : self.text(),
                Vision.Key.PARENT_ID    : self.parentId(),
                Vision.Key.ROOT_ID      : self.rootId(),
                Vision.Key.PRIVACY      : self.privacy(),
               }

    def toDictionaryDeep(self):
        '''Used for packaging into JSON

        If accessing many visions, use VisionList instead! It can batch up
        DB queries across visions for better performance
        '''
        obj = self.toDictionary()
        picture = self.picture()
        if picture:
            obj[Vision.Key.PICTURE] = picture.toDictionary()
        return obj

    #
    # Private methods
    #
    def __init__(self, model):
        assert model, "Invalid vision model"
        self._model = model

    @staticmethod
    def _getByModel(model):
        '''*** DON'T USE THIS: used internally within API for now ***'''
        return Vision(model)

# $eof
