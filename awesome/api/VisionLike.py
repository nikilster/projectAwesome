from data.DataApi import DataApi

from ..util.Logger import Logger

class VisionLike:
    '''For fetching and setting vision likes'''
    #
    # Static methods
    #

    @staticmethod
    def get(vision, user):
        '''Get VisionLike or None'''
        model = DataApi.getVisionLike(vision.model(), user.model())
        if model == DataApi.NO_OBJECT_EXISTS:
            return None
        return VisionLike(model)

    @staticmethod
    def getCount(vision):
        '''Get number of likes for a given vision'''
        return DataApi.getVisionLikeCount(vision.model())


    #
    # Getters
    #
    def id(self):
        return self._model.id
    def visionId(self):
        return self._model.visionId
    def userId(self):
        return self._model.userId

    #
    # Private methods: Don't use these externally
    #
    def __init__(self, model):
        assert model != None, "Invalid model for vision like"

# eof
