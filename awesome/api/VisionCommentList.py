from data.DataApi import DataApi

from VisionComment import VisionComment

from ..util.Logger import Logger

class VisionCommentList:
    '''For getting properties about a list of vision comments.'''

    #
    # Static methods to get a list of comments
    #

    @staticmethod
    def getFromVision(vision, maxComments):
        '''Get comment list from vision with max number, else None.

        NOTE: This assumes the user is vetted to access this vision.
        '''
        models  = DataApi.getVisionComments(vision.id(), maxComments)
        return VisionCommentList._getWithModels(models)

    @staticmethod
    def getEmptyList():
        return VisionCommentList([])

    @staticmethod
    def _getWithModels(models):
        '''Don't use! Used internally with API'''
        return VisionCommentList(models)

    #
    # Getters
    #

    def comments(self):
        return [VisionComment._getByModel(m) for m in self._commentModels]
    def length(self):
        return len(self._commentModels)

    def toDictionaryDeep(self):
        '''For packaging JSON objects
        
        Deep call accesses DB again for other objects so don't use unless
        necessary.
        '''
        objs = []
        commentList = self._commentModels

        if self.length() > 0:
            authorIds = set([comment.authorId() for comment in self.comments()])
            authors = DataApi.getUsersFromIds(authorIds)
            idToAuthor = dict([(user.id, user) for user in authors])

            for comment in commentList:
                obj = VisionComment(comment).toDictionary()
                author = idToAuthor[comment.authorId]

                obj[VisionComment.Key.NAME] = author.fullName
                obj[VisionComment.Key.PICTURE] = author.picture

                objs.append(obj)
        return objs

    #
    # Private
    #

    def __init__(self, commentModels):
        '''Private: don't use'''
        self._commentModels = commentModels

# $eof
