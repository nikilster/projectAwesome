from data.DataApi import DataApi

from Vision import Vision
from VisionComment import VisionComment
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
        models = DataApi.getVisionsForUser(userId, targetUser.id())

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
    def getWithVision(vision):
        '''Create a vision list with a single vision.

        Is here to leverage output functions here, even if for just one 
        vision
        '''
        assert vision, "Invalid vision"
        return VisionList([vision._getModel()])

    #Returns a seleted vision per user
    #Used for motivation emails
    @staticmethod
    def visionPerUser():
        pass

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

    def randomVision(self):
        if self.length() > 0:
            return random.choice(self.visions())
        return None

    def toDictionaryDeep(self):
        '''For packaging to JSON output.
        
        This batches up queries for pictures and comments across all the
        visions. Whenever we want to get all this data across a list of 
        visions, it is good to use VisionList instead of the
        toDictionaryDeep calls in other objects.
        '''
        visions = [vision._model for vision in self.visions()]
        visionList = []

        pictureIds = set([vision.pictureId for vision in visions])
        pictureIds.discard(0)
        pictures = DataApi.getPicturesFromIds(pictureIds)
        idToPicture = dict([(picture.id, picture) for picture in pictures])
        idToPicture[0] = ""

        userIds = set([vision.userId for vision in visions])
        users = DataApi.getUsersFromIds(userIds)
        idToUser = dict([(user.id, user) for user in users])

        # TODO: this isn't fast, but will do for now.
        visionIds = [vision.id for vision in visions]
        comments = list()
        for visionId in visionIds:
            comments.extend(DataApi.getVisionComments(visionId, 4))

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
            obj = Vision(vision).toDictionary()
            obj[Vision.Key.NAME] = idToUser[vision.userId].fullName
            if vision.pictureId != 0:
                picture = Picture(idToPicture[vision.pictureId]).toDictionary()
                obj[Vision.Key.PICTURE] = picture
            obj['comments'] = []
            if vision.id in idToComments.keys():
                for comment in idToComments[vision.id]:
                    commentObj = VisionComment(comment).toDictionary()
                    author = idToAuthor[comment.authorId]
                    commentObj[VisionComment.Key.NAME] = author.fullName
                    commentObj[VisionComment.Key.PICTURE] = author.picture
                    obj[Vision.Key.COMMENTS].append(commentObj)
            visionList.append(obj)
        return visionList

    #
    # Private
    #
    def __init__(self, visionModels):
        '''Private: do not use.'''
        self._visions = [Vision(model) for model in visionModels]

# $eof
