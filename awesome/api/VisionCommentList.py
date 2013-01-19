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
        models  = DataApi.getVisionComments(vision.model(), maxComments)
        return VisionCommentList._getWithModels(models)

    @staticmethod
    def getEmptyList():
        return VisionCommentList(list())

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

    def toDictionary(self, options=[], user=None):
        '''For packaging JSON objects
        
        Pass in list of VisionComment.Options.* for extra information
        '''
        objs = []
        commentList = self._commentModels

        if self.length() > 0:
            if VisionComment.Options.AUTHOR in options:
                authorIds = set([comment.authorId()
                                                for comment in self.comments()])
                authors = DataApi.getUsersFromIds(authorIds)
                idToAuthor = dict([(u.id, u) for u in authors])

            # If LIKES
            if VisionComment.Options.LIKES in options:
                commentIds = [c.id() for c in self.comments()]
                tuples = DataApi.getVisionCommentListLikeCount(commentIds)
                idToLikeCount = dict([(commentId, count)
                                       for commentId, count in tuples])
                if user:
                    commentUserLikes = DataApi.getVisionCommentIdsLikedByUser(
                                                        commentIds, user.id())

            for comment in commentList:
                obj = VisionComment(comment).toDictionary()
                if VisionComment.Options.AUTHOR in options:
                    from User import User
                    author = idToAuthor[comment.authorId]
                    obj[VisionComment.Key.AUTHOR] = User(author).toDictionary()
                    # If LIKES
                    if VisionComment.Options.LIKES in options:
                        obj[VisionComment.Key.LIKE] = \
                                    { VisionComment.Key.LIKE_COUNT :
                                      idToLikeCount[comment.id] if
                                      comment.id in idToLikeCount else 0 }
                        if user:
                            obj[VisionComment.Key.LIKE]\
                               [VisionComment.Key.USER_LIKE] =\
                                                comment.id in commentUserLikes
                objs.append(obj)
        return objs

    def extend(self, commentList):
        '''Appends commentList parameter to this vision comment list'''
        self._commentModels.extend(commentList._commentModels)

    #
    # Private
    #

    def __init__(self, commentModels):
        '''Private: don't use'''
        self._commentModels = commentModels

# $eof
