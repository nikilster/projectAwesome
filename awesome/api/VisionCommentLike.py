from data.DataApi import DataApi

from ..util.Logger import Logger

class VisionCommentLike:
    '''For fetching and setting vision comment likes'''
    #
    # Static methods
    #

    @staticmethod
    def get(comment, user):
        '''Get VisionCommentLike or None'''
        if user == None:
            return None
        model = DataApi.getVisionCommentLike(comment.model(), user.model())
        if model == DataApi.NO_OBJECT_EXISTS:
            return None
        return VisionCommentLike(model)

    @staticmethod
    def getCount(comment):
        '''Get number of likes for a given comment'''
        return DataApi.getVisionCommentLikeCount(comment.model())

    @staticmethod
    def getCount():
        '''Gets count of vision likes'''
        return DataApi.getVisionCommentLikeCount()

    @staticmethod
    def getLikes(comment, limit=100):
        '''Get list of VisionCommentLikes'''
        models = DataApi.getVisionCommentLikes(comment.model(), limit)
        return [VisionCommentLike(model) for model in models]

    #
    # Getters
    #
    def id(self):
        return self._model.id
    def visionCommentId(self):
        return self._model.visionCommentId
    def userId(self):
        return self._model.userId

    #
    # Private methods: Don't use these externally
    #
    def __init__(self, model):
        assert model != None, "Invalid model for vision comment like"
        self._model = model

# $eof
