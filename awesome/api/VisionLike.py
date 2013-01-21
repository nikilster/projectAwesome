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
    def getLikes(vision, limit=100):
        '''Get list of VisionLikes'''
        models = DataApi.getVisionLikes(vision.model(), limit)
        return [VisionLike(model) for model in models]

    @staticmethod
    def getCountForVision(vision):
        '''Get number of likes for a given vision'''
        return DataApi.getVisionLikeCountForVision(vision.model())

    @staticmethod
    def getCount():
        '''Gets count of vision likes'''
        return DataApi.getVisionLikeCount()


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
        self._model = model

# eof
