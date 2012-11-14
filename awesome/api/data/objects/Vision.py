'''
	Vision

	This model stores the information for a vision data object

	Fields:
		id
		userId
		text
		pictureId
		parent
		dateCreated
'''

#Parent Class
from Data import Data

class Vision(Data):

	#Fields in the Vision model
	VISION_FIELDS = ['id', 'userId', 'text', 'pictureId', 'dateCreated', 'parentId']

	#Load the object from json
	def setFromJson(self, jsonData):
		
		#Parent Function
		Data.setFromJson(self, jsonData, Vision.VISION_FIELDS)		

	#Used when creating the object to put in the database
	def setInfo(self, id, userId, text, pictureId, parentId, dateCreated):

		#Todo: do this in loop
		self.id = id
		self.userId = userId
		self.text = text
		self.pictureId = pictureId
		self.dateCreated = dateCreated
		self.parentId = parentId

	#Set the Picture Object
	def setPicture(self, picture):
		self.picture = picture