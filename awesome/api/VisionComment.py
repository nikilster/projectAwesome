from data.DataApi import DataApi

from VisionCommentLike import VisionCommentLike

from ..util.Logger import Logger


class VisionComment:
    '''For getting properties about vision comments.'''

    #
    # Constants, enums
    #
    class Key:
        ''' For dictionary use'''
        ID = 'id'
        VISION_ID = 'visionId'
        AUTHOR_ID = 'authorId'
        TEXT = 'text'
        CREATED = 'created'
        # These are included when Options.AUTHOR is passed
        AUTHOR = 'author'
        # Options.LIKES
        LIKE = 'like'
        # - these keys are used within Vision.Key.LIKE object
        USER_LIKE = 'userLike'
        LIKE_COUNT = 'likeCount'

    class Options:
        AUTHOR = 'author'
        LIKES = 'likes'

    #
    # Static methods to get Comment
    #

    @staticmethod
    def getById(visionCommentId):
        '''Gets by ID. MUST remember to check if access to Vision is OK.'''
        model = DataApi.getVisionComment(visionCommentId)
        if DataApi.NO_OBJECT_EXISTS == model:
            return None
        return VisionComment(model)

    
    @staticmethod
    def _getByModel(model):
        '''This is used internally within API. Try not to use this.'''
        return VisionComment(model)


    #
    # Getter methods
    #
    def id(self):
        return self._model.id
    def visionId(self):
        return self._model.visionId
    def authorId(self):
        return self._model.authorId
    def text(self):
        return self._model.text
    def removed(self):
        return self._model.removed
    def created(self):
        return self._model.created
    def model(self):
        return self._model

    #
    # Getter methods
    #
    def author(self):
        from User import User
        return User.getById(self.authorId())

    def vision(self, inquiringUser):
        from Vision import Vision
        return Vision.getById(self.visionId(), inquiringUser)

    def toDictionary(self, options=[], user=None):
        '''For packaging in JSON objects.
        
        Pass in list of VisionComment.Options.* to include other info in objs
        '''
        obj = {  VisionComment.Key.ID : self.id(),
                 VisionComment.Key.VISION_ID : self.visionId(),
                 VisionComment.Key.AUTHOR_ID : self.authorId(),
                 VisionComment.Key.TEXT : self.text(),
                 VisionComment.Key.CREATED: self.created().isoformat(),
              }
        if VisionComment.Options.AUTHOR in options:
            from User import User
            obj = self.toDictionary()
            author = User.getById(self.authorId())
            if author:
                obj[VisionComment.Key.AUTHOR] = author.toDictionary()
        if VisionComment.Options.LIKES in options:
            obj[VisionComment.Key.LIKE] = { 
                                VisionComment.Key.LIKE_COUNT: self.likeCount() }
            if user:
                obj[VisionComment.Key.LIKE][VisionComment.Key.USER_LIKE] = \
                                                            self.likedBy(user)
        return obj

    #
    # Like methods
    #

    def likeCount(self):
        return VisionCommentLike.getCount(self)

    def getLike(self, user):
        '''Returns VisionCommentLike or None'''
        return VisionCommentLike.get(self, user)

    def likedBy(self, user):
        '''Returns True of user likes vision comment, else False.'''
        like = self.getLike(user)
        return like != None

    def getLikes(self):
        '''Returns list of VisionCommentLikes'''
        return VisionCommentLike.getLikes(self)

    def getLikesUserList(self):
        '''Returns list of Users that like this comment'''
        likes = self.getLikes()
        from UserList import UserList
        return UserList.getByUserIds([like.userId() for like in likes])

    def like(self, user):
        '''Returns true if successful, false otherwise'''
        like = DataApi.addVisionCommentLike(self.model(), user.model())
        if like:
            # If liker different than author, email the author of the comment
            if user.id() != self.authorId():
                from ..WorkerJobs import Queue_visionCommentLikeEmail
                author = self.author()
                if author:
                    vision = self.vision(user)
                    if vision:
                        Queue_visionCommentLikeEmail(
                                            author.toDictionaryFull(),
                                            user.toDictionary(),
                                            vision.toDictionary(),
                                            self.toDictionary())
            return True
        return False

    def unlike(self, user):
        '''Returns true if successful, false otherwise'''
        return DataApi.removeVisionCommentLike(self.model(), user.model())


    #
    # Private methods
    #
    def __init__(self, model):
        assert model, "Invalid comment model"
        self._model = model

# $eof
