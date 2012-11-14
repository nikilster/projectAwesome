'''
	Picture

	Model / Object which represents a photo in the system

	A vision has a picture

	Extends: Data (Class)

	Fields
		id
		url
		filename

'''

from Data import Data

class Picture(Data):

    PICTURE_FIELDS = ['id', 'url', 'filename']

    #Load the object from json
    def setFromJson(self, jsonData):

        #Parent class function
        Data.setFromJson(self, jsonData, Picture.PICTURE_FIELDS)


    #Init when creating a Picture
    def setInfo(self, id, url, filename):
        self.id = id
        self.url = url
        self.filename = filename