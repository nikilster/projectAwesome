from data.DataApi import DataApi

from ..util.Logger import Logger

class Picture:
    '''For getting properties about pictures.
    *** IMPORTANT NOTE ***
    - Pictures are currently _created_ in the Vision class. This is because
      for now, we only ever create a picture in the process of creating an
      Vision. 
    '''

    #
    # Constants, enums
    #
    class Key:
        ''' For dictionary use'''
        ID = 'id'
        LARGE_URL = "largeUrl"
        LARGE_WIDTH = "largeWidth"
        LARGE_HEIGHT = "largeHeight"
        MEDIUM_URL = "mediumUrl"
        MEDIUM_WIDTH = "mediumWidth"
        MEDIUM_HEIGHT = "mediumHeight"
        SMALL_URL = "smallUrl"
        SMALL_WIDTH = "smallWidth"
        SMALL_HEIGHT = "smallHeight"


    #
    # Static methods to get a vision
    #
    @staticmethod
    def getById(pictureId):
        '''Get picture by id, else None'''
        if pictureId > 0:
            model = DataApi.getPicture(pictureId)
            if DataApi.NO_OBJECT_EXISTS != model:
                return Picture(model)
        return None

    @staticmethod
    def getByIds(pictureIds):
        '''Get list of Pictures from picture ids.'''
        models = DataApi.getPicturesFromIds(pictureIds)
        return [Picture(model) for model in models]

    #
    # Getters
    #
    def id(self):
        return self._model.id
    def userId(self):
        return self._model.userId

    def filename(self):
        '''URL (if used bookmarklet) or filename (if uploaded)'''
        return self._model.original
    def uploaded(self):
        '''True if uploaded, False if from internet (w/ bookmarklet)'''
        return self._model.uploaded

    def s3Bucket(self):
        return self._model.s3Bucket

    def origKey(self):
        return self._model.origKey
    def origWidth(self):
        return self._model.origWidth
    def origHeight(self):
        return self._model.origHeight
    def origUrl(self):
        return self._model.origUrl

    def largeKey(self):
        return self._model.largeKey
    def largeWidth(self):
        return self._model.largeWidth
    def largeHeight(self):
        return self._model.largeHeight
    def largeUrl(self):
        return self._model.largeUrl

    def mediumKey(self):
        return self._model.mediumKey
    def mediumWidth(self):
        return self._model.mediumWidth
    def mediumHeight(self):
        return self._model.mediumHeight
    def mediumUrl(self):
        return self._model.mediumUrl

    def smallKey(self):
        return self._model.smallKey
    def smallWidth(self):
        return self._model.smallWidth
    def smallHeight(self):
        return self._model.smallHeight
    def smallUrl(self):
        return self._model.smallUrl

    def removed(self):
        return self._model.removed


    def toDictionary(self):
        '''For using to package up JSON.'''
        return { Picture.Key.ID         : self.id(),
                 Picture.Key.LARGE_URL  : self.largeUrl(),
                 Picture.Key.LARGE_WIDTH : self.largeWidth(),
                 Picture.Key.LARGE_HEIGHT : self.largeHeight(),
                 Picture.Key.MEDIUM_URL : self.mediumUrl(),
                 Picture.Key.MEDIUM_WIDTH : self.mediumWidth(),
                 Picture.Key.MEDIUM_HEIGHT : self.mediumHeight(),
                 Picture.Key.SMALL_URL  : self.smallUrl(),
                 Picture.Key.SMALL_WIDTH : self.smallWidth(),
                 Picture.Key.SMALL_HEIGHT : self.smallHeight()
               }

    #
    # Private methods
    #
    def __init__(self, model):
        '''Private: do not use!'''
        assert model, "Invalid picture model"
        self._model = model

# $eof
