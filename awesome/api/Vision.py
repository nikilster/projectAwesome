from data.DataApi import DataApi

from VisionComment import VisionComment
from VisionCommentList import VisionCommentList
from Picture import Picture
from Privacy import Relationship, VisionPrivacy
from VisionLike import VisionLike

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
        CREATED = 'created'
        # These are filled when proper options are passed in
        PICTURE = 'picture'
        PARENT_USER = 'parentUser'
        LIKE = 'like'
        # - these keys are used within Vision.Key.LIKE object
        USER_LIKE = 'userLike'
        LIKE_COUNT = 'likeCount'
        # With USER Option
        USER = 'user'
        # These are used externally
        COMMENTS = 'comments'
        REPOST_USERS = 'repostUsers'
    
    class Options:
        '''Extra options to pass to toDictionary'''
        PICTURE = 0
        PARENT_USER = 1
        LIKES = 2
        USER = 3
        # Only used in VisionList.toDictionary so far
        COMMENTS = 4
        COMMENT_LIKES = 5
    
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
    def created(self):
        return self._model.created
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

    def parentVision(self, inquiringUser):
        '''Returns root vision, else None'''
        if not self.isOriginalVision():
            return Vision.getById(self.parentId(), inquiringUser)
        return None

    def rootVision(self, inquiringUser):
        '''Returns root vision, else None'''
        if not self.isRootVision():
            return Vision.getById(self.rootId(), inquiringUser)
        return None

    def reposts(self):
        '''Get last 5 public vision reposts'''
        from VisionList import VisionList
        return VisionList.getVisionReposts(self)

    def repostUsers(self):
        reposts = self.reposts()
        userIds = set()
        users = []
        if reposts.length() > 0:
            from User import User
            for vision in reposts.visions():
                userIds.add(vision.userId())
            users = User.getByUserIds(userIds)
        return users

    def edit(self, text, isPublic):
        '''Set new text and/or privacy value
       
        Returns (True if change happened, error_msg if there is one)
        '''
        # Make sure text is valid
        text = text.strip()
        if len(text) < 0:
            return (False, "Text field is required.")

        # Make sure to maintain privacy! If already private, can't change to
        # public!
        if False == self.isPublic() and \
           True == isPublic and \
           DataApi.visionHasCommentsFromOthers(self.model(), self.userId()):
            return (False,
                    "Can't make vision public once there are comments from others.")
        # ok, now we can make the change
        privacy = VisionPrivacy.PRIVATE
        if isPublic:
            privacy = VisionPrivacy.PUBLIC
        return (DataApi.editVision(self.model(), text, privacy), "")

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

    def toDictionary(self, options=[], user=None):
        '''Used for packaging into JSON
        
        Pass in optional input list with other things to package into object.

        If accessing many visions, use VisionList instead! It can batch up
        DB queries across visions for better performance

        The 'user' parameter is used when LIKES option is provided to
        determine whether this vision is liked by the user
        '''
        obj = { Vision.Key.ID           : self.id(),
                Vision.Key.USER_ID      : self.userId(),
                Vision.Key.TEXT         : self.text(),
                Vision.Key.PARENT_ID    : self.parentId(),
                Vision.Key.ROOT_ID      : self.rootId(),
                Vision.Key.PRIVACY      : self.privacy(),
                Vision.Key.CREATED      : self.created().isoformat(),
              }
        from User import User
        if Vision.Options.PICTURE in options:
            picture = self.picture()
            if picture:
                obj[Vision.Key.PICTURE] = picture.toDictionary()
        if Vision.Options.USER in options:
            user = User.getById(self.userId())
            if user:
                obj[Vision.Key.USER] = user.toDictionary()
        if Vision.Options.PARENT_USER in options:
            if not self.isOriginalVision():
                parentVision = Vision.getById(self.parentId(), self)
                # Parent vision MUST be public
                if parentVision and parentVision.isPublic():
                    parentUser = User.getById(parentVision.userId())
                    if parentUser:
                        obj[Vision.Key.PARENT_USER] = parentUser.toDictionary()
        if Vision.Options.LIKES in options:
            obj[Vision.Key.LIKE] = { Vision.Key.LIKE_COUNT: self.likeCount() }
            if user:
                obj[Vision.Key.LIKE][Vision.Key.USER_LIKE] = self.likedBy(user)
        return obj

    #
    # Like methods
    #

    def likeCount(self):
        return VisionLike.getCount(self)

    def getLike(self, user):
        '''Returns VisionLike or None'''
        return VisionLike.get(self, user)

    def likedBy(self, user):
        '''Returns True of user likes vision, else False.'''
        like = self.getLike(user)
        return like != None

    def like(self, user):
        '''Returns true if successful, false otherwise'''
        like = DataApi.addVisionLike(self.model(), user.model())
        if like:
            # If liker is different from owner of vision, email the owner
            if user.id() != self.userId():
                from ..WorkerJobs import Queue_visionLikeEmail
                owner = self.user()
                if owner:
                    Queue_visionLikeEmail(owner.toDictionaryFull(),
                                          user.toDictionary(),
                                          self.toDictionary())
            return True
        return False
    def unlike(self, user):
        '''Returns true if successful, false otherwise'''
        return DataApi.removeVisionLike(self.model(), user.model())

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
