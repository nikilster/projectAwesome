###############################################################################
# VisionComment
#
# This is the VisionComment abstraction that should be used for getting
# properties about vision comments.
#
# *** IMPORTANT NOTE ***
#   - Pictures are currently _created_ in the Vision class. This is because
#     for now, we only ever create a picture in the process of creating an
#     Vision. 
#
###############################################################################
from data.DataApi import DataApi

from ..util.Logger import Logger

class Picture:
    #
    # Static methods to get a vision
    #
    @staticmethod
    def getById(pictureId):
        if pictureId > 0:
            model = DataApi.getPicture(pictureId)
            if DataApi.NO_OBJECT_EXISTS != model:
                return Picture(model)
        return None

    #
    # Getters
    #
    def id(self):
        return self._model.id
    def userId(self):
        return self._model.userId

    # original filename: URL (if used bookmarklet) or filename (if uploaded)
    def filename(self):
        return self._model.original
    # True if picture uploaded, and False if from internet (w/ bookmarklet)
    def uploaded(self):
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


    # For using to package up JSON
    def toDictionary(self):
        return { 'id' : self.id(),
                 'largeUrl' : self.largeUrl(),
                 'mediumUrl' : self.mediumUrl(),
                 'smallUrl' : self.smallUrl(),
               }

    #
    # Private methods
    #
    def __init__(self, model):
        assert model, "Invalid picture model"
        self._model = model

# $eof
