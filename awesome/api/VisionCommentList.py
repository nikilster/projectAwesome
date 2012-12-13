from data.DataApi import DataApi

from VisionComment import VisionComment

from ..util.Logger import Logger

class VisionCommentList:
    '''For getting properties about a list of vision comments.'''

    #
    # Static methods to get a list of comments
    #

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
                obj['name'] = idToAuthor[comment.authorId].fullName
                obj['picture'] = idToAuthor[comment.authorId].picture
                objs.append(obj)
        return objs

    #
    # Private
    #

    def __init__(self, commentModels):
        '''Private: don't use'''
        self._commentModels = commentModels

# $eof
