from data.DataApi import DataApi

from Vision import Vision
from VisionComment import VisionComment
from Picture import Picture

from ..util.Logger import Logger

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
        return VisionList(models)

    @staticmethod
    def getWithVision(vision):
        '''Create a vision list with a single vision.

        Is here to leverage output functions here, even if for just one 
        vision
        '''
        assert vision, "Invalid vision"
        return VisionList([vision._getModel()])

    #
    # Getters
    #
    def visions(self):
        '''Returns array of visions.'''
        return [Vision(model) for model in self._visionModels]

    def toDictionaryDeep(self):
        '''For packaging to JSON output.
        
        This batches up queries for pictures and comments across all the
        visions. Whenever we want to get all this data across a list of 
        visions, it is good to use VisionList instead of the
        toDictionaryDeep calls in other objects.
        '''
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
            obj = Vision(vision).toDictionary()
            obj['name'] = idToUser[vision.userId].fullName
            if vision.pictureId != 0:
                obj['picture'] = Picture(idToPicture[vision.pictureId]).toDictionary()
            obj['comments'] = []
            if vision.id in idToComments.keys():
                for comment in idToComments[vision.id]:
                    commentObj = VisionComment(comment).toDictionary()
                    author = idToAuthor[comment.authorId]
                    commentObj['name'] = author.fullName
                    commentObj['picture'] = author.picture
                    obj['comments'].append(commentObj)
            visionList.append(obj)
        return visionList

    #
    # Private
    #
    def __init__(self, visionModels):
        '''Private: do not use.'''
        self._visionModels = visionModels

# $eof
