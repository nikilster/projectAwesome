from data.DataApi import DataApi

from Vision import Vision
from VisionComment import VisionComment
from VisionCommentList import VisionCommentList
from Picture import Picture
from Privacy import Relationship, VisionPrivacy

from ..util.Logger import Logger

import random

class VisionList:
    '''For getting/using different types of vision lists.
    
    This class will commonly be used for getting different collections of
    visions, and then producing some kind of output for email or JSON.

    *** IMPORTANT NOTES ***
    - All methods on visions which affect the user's vision list order should
      NOT be here. This is because currently the Vision and VisionList
      classes do not know anything about a user's vision list order.

    - Check out the User object to create, add, move, repost visions!!!!!!!
    - ONLY use this for getting lists of visions (w/o need for user vision
      list order)
    '''

    #
    # Static methods to get vision lists
    #

    @staticmethod
    def getMainPageVisions():
        '''Gets most recently created public visions'''
        models = DataApi.getMainPageVisions()
        return VisionList(models)

    @staticmethod
    def getUserVisions(user, targetUser):
        '''Gets vision of targetUser that are accessible by user.
        
        If user is None, it will treat it as public access.
        '''
        assert targetUser, "Invalid target user"
        userId = None
        if user:
            userId = user.id()
        models = DataApi.getVisionsForUser(targetUser.model())

        # determine relationship for filtering viewable visions
        relationship = Relationship.get(userId, targetUser.id())

        if Relationship.NONE == relationship:
            # If no relationship, only show public visions
            filtered = []
            for model in models:
                if model.privacy == VisionPrivacy.PUBLIC:
                    filtered.append(model)
            return VisionList(filtered)
        elif Relationship.SELF == relationship:
            # Show all visions
            return VisionList(models)
        else:
            assert False, "Invalid relationship value"
            return None

    @staticmethod
    def getByIds(visionIds):
        '''Note that this assumes we have access to all these visions.

        MUST do privacy checks before calling.
        '''
        models = DataApi.getVisionsById(visionIds)
        return VisionList(models)

    @staticmethod
    def getVisionReposts(vision):
        '''Gets last 5 public vision reposts'''
        models = DataApi.getVisionReposts(vision.model())
        return VisionList(models)
    
    @staticmethod
    def createFromVision(vision):
        '''Create a vision list with a single vision.

        Is here to leverage output functions here, even if for just one 
        vision
        '''
        assert vision, "Invalid vision"
        return VisionList([vision.model()])


    #
    # Getters
    #
    def visions(self):
        '''Returns array of visions.'''
        return self._visions

    #
    # Utility methods
    #
    def length(self):
        return len(self.visions())

    def limitLength(self, limit):
        if limit > 0 and self.length() > limit:
            self._visions = self._visions[0:limit]

    def randomVision(self):
        if self.length() > 0:
            return random.choice(self.visions())
        return None

    def toDictionary(self, options=[], user=None):
        '''For packaging to JSON output.

        options input is list of Vision.Options when we want more information
        fetched from DB and placed into objects
       
        This batches up queries for pictures and comments across all the
        visions. Whenever we want to get all this data across a list of 
        visions, it is good to use VisionList.toDictionary() instead of the
        individual toDictionary() calls on objects.

        'user' parameter is only used when LIKES in provided as
        an option. If it is passed in, we also check whether this user likes
        the visions or not.
        '''
        from User import User

        retObj = []

        # Get pictures and hash if we want them
        if Vision.Options.PICTURE in options:
            pictureIds = set([vision.pictureId() for vision in self.visions()])
            pictureIds.discard(0)
            pictures = Picture.getByIds(pictureIds)
            idToPicture = dict([(picture.id(), picture)
                                                      for picture in pictures])
            idToPicture[0] = ""

        # Get parent users if we need them
        parentUserIds = set()
        if Vision.Options.PARENT_USER in options:
            parentVisionIds = set([vision.parentId()
                                                 for vision in self.visions()])
            parentVisionIds.discard(0)
            parentVisions = VisionList.getByIds(parentVisionIds)
            idToParentVisions = dict([(v.id(), v)
                                             for v in parentVisions.visions()])
            parentUserIds = set([parent.userId()
                                        for parent in parentVisions.visions()])

        # Get all users (including parent users if needed)
        userIds = set([vision.userId() for vision in self.visions()])
        users = User.getByUserIds(userIds.union(parentUserIds))
        idToUser = dict([(u.id(), u) for u in users])

        # If COMMENTS, get comments
        if Vision.Options.COMMENTS in options:
            commentList = VisionCommentList.getEmptyList()
            for vision in self.visions():
                # TODO: Speed up performance of this some time!
                commentList.extend(vision.comments(5))

            idToComments = {}
            for comment in commentList.comments():
                if not comment.visionId() in idToComments:
                    idToComments[comment.visionId()] = [comment]
                else:
                    idToComments[comment.visionId()].append(comment)

            authorIds = set([comment.authorId() 
                                        for comment in commentList.comments()])
            authors = User.getByUserIds(authorIds)
            idToAuthor = dict([(author.id(), author) for author in authors])

            # If COMMENT_LIKES
            if Vision.Options.COMMENT_LIKES in options:
                commentIds = [c.id() for c in commentList.comments()]
                tuples = DataApi.getVisionCommentListLikeCount(commentIds)
                idToCommentLikes = dict([(commentId, count)
                                                for commentId, count in tuples])
                if user:
                    commentUserLikes = DataApi.getVisionCommentIdsLikedByUser(
                                                        commentIds, user)

        # If LIKES, get vision likes in batch
        if Vision.Options.LIKES in options:
            visionIds = [v.id() for v in self.visions()]
            tuples = DataApi.getVisionListLikeCount(visionIds)
            idToLikes = dict([(visionId, count) for visionId, count in tuples])
            if user:
                userLikes = DataApi.getVisionIdsLikedByUser(visionIds,
                                                            user.id())

        # Now start building object list to return
        for vision in self.visions():
            obj = vision.toDictionary()
            obj[Vision.Key.NAME] = idToUser[vision.userId()].fullName()

            # If PICTURE
            if Vision.Options.PICTURE in options:
                if vision.pictureId != 0:
                    picture = idToPicture[vision.pictureId()].toDictionary()
                    obj[Vision.Key.PICTURE] = picture
            # If COMMENTS
            if Vision.Options.COMMENTS in options:
                obj[Vision.Key.COMMENTS] = []
                if vision.id() in idToComments:
                    for comment in idToComments[vision.id()]:
                        commentObj = comment.toDictionary()
                        author = idToAuthor[comment.authorId()]
                        commentObj[VisionComment.Key.NAME] = author.fullName()
                        commentObj[VisionComment.Key.PICTURE] = author.picture()

                        if Vision.Options.COMMENT_LIKES in options:
                            commentObj[VisionComment.Key.LIKE] = {
                                            VisionComment.Key.LIKE_COUNT:
                                            idToCommentLikes[comment.id()]
                                            if comment.id() in idToCommentLikes
                                            else 0 }
                            if user:
                                commentObj[VisionComment.Key.LIKE]\
                                          [VisionComment.Key.USER_LIKE] = \
                                            comment.id() in commentUserLikes
                        obj[Vision.Key.COMMENTS].append(commentObj)

            # If PARENT_USER
            if Vision.Options.PARENT_USER in options:
                if not vision.isOriginalVision():
                    if vision.parentId() in idToParentVisions:
                        parentVision = idToParentVisions[vision.parentId()]
                        if parentVision.userId() in idToUser:
                            parentUser = idToUser[parentVision.userId()]
                            obj[Vision.Key.PARENT_USER] = \
                                                     parentUser.toDictionary()
            # If LIKES
            if Vision.Options.LIKES in options:
                obj[Vision.Key.LIKE] = { Vision.Key.LIKE_COUNT: 
                                         idToLikes[vision.id()]
                                         if vision.id() in idToLikes else 0 }
                if user:
                    obj[Vision.Key.LIKE][Vision.Key.USER_LIKE] = \
                                                    vision.id() in userLikes

            # finally append object to list
            retObj.append(obj)
        return retObj


    #
    # Private
    #
    def __init__(self, visionModels):
        '''Private: do not use.'''
        self._visions = [Vision(model) for model in visionModels]

# $eof
