'''
	User

	Model / Object which represents a user in the system

	Extends: Data (Class)

	Fields:
			id
			email
			dateCreated
			password
'''

#Parent Class
from Data import Data

class User(Data):

	#The fields in the user model
	#TODO: Best way to do this? check this
	USER_FIELDS = ['id', 'firstName', 'lastName', 'email', 'dateCreated', 'password']

	#Load the object from json
	def setFromJson(self, jsonData):

		#Parent function
		Data.setFromJson(self, jsonData, User.USER_FIELDS)
	


	#Init when creating a user
	def setInfo(self, id, firstName, lastName, email, password, dateCreated):
		self.id = id
		self.firstName = firstName
		self.lastName = lastName
		self.email = email
		self.password = password
		self.dateCreated = dateCreated
