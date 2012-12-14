from data.DataApi import DataApi

from ..util.Logger import Logger

class VisionComment:
    '''For getting properties about vision comments.'''

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
        return { 'id' : self.id(),
                 'visionId' : self.visionId(),
                 'authorId' : self.authorId(),
                 'text' : self.text(),
               }

    def toDictionaryDeep(self):
        '''For packaging in JSON objects.
        
        Accesses DB again so don't use if possible.
        '''
        from User import User
        obj = self.toDictionary()
        author = User.getById(self.authorId())
        if author:
            obj['name'] = author.fullName()
            obj['picture'] = author.picture()
        return obj

    #
    # Private methods
    #
    def __init__(self, model):
        assert model, "Invalid comment model"
        self._model = model

# $eof
