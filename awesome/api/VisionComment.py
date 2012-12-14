from data.DataApi import DataApi

from ..util.Logger import Logger

class VisionComment:
    '''For getting properties about vision comments.'''

    #
    # Constants, enums
    #
    class Key:
        ''' For dictionary use'''
        ID = 'id'
        VISION_ID = 'visionId'
        AUTHOR_ID = 'authorId'
        TEXT = 'text'
        # These aren't always there
        NAME = 'name'
        PICTURE = 'picture'

    #
    # Static methods to get Comment
    #

    @staticmethod
    def _getByModel(model):
        '''This is used internally within API. Try not to use this.'''
        return VisionComment(model)


    #
    # Getter methods
    #
    def id(self):
        return self._model.id
    def visionId(self):
        return self._model.visionId
    def authorId(self):
        return self._model.authorId
    def text(self):
        return self._model.text
    def removed(self):
        return self._model.removed

    #
    # Getter methods
    #
    def author(self):
        from User import User
        return User.getById(self.authorId())

    def toDictionary(self):
        '''For packaging in JSON objects.'''
        return { VisionComment.Key.ID : self.id(),
                 VisionComment.Key.VISION_ID : self.visionId(),
                 VisionComment.Key.AUTHOR_ID : self.authorId(),
                 VisionComment.Key.TEXT : self.text(),
               }

    def toDictionaryDeep(self):
        '''For packaging in JSON objects.
        
        Accesses DB again so don't use if possible.
        '''
        from User import User
        obj = self.toDictionary()
        author = User.getById(self.authorId())
        if author:
            obj[VisionComment.Key.NAME] = author.fullName()
            obj[VisionComment.Key.PICTURE] = author.picture()
        return obj

    #
    # Private methods
    #
    def __init__(self, model):
        assert model, "Invalid comment model"
        self._model = model

# $eof
