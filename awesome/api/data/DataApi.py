'''
	Class: Data API

	Main api for data

	Functions:

		Add User
		Add Vision
		Get Visions for User
		Get Main Page Visions

'''


'''
	Creates and adds the user to the database

'''

#TODO: Figure out a better way to do this!
#add the object directory to path
# (relative paths)
import os
import sys
dir = os.path.dirname(__file__)
OBJECT_FILES_PATH = os.path.join(dir, 'objects')
sys.path.append(OBJECT_FILES_PATH)

from User import User
from Vision import Vision
from DB import DB

#For date created
from time import time

class DataApi:

	@staticmethod
	def addUser(firstName, lastName, email, password):

		#TODO: Validate

		#Init (create) Db
		db = DB() 

		#Create User Object
		#Get the next id from redis
		newUser = User()
		newUser.setInfo(db.getNextUserId(), firstName, lastName, email, password, time())

		#Save
		#TODO: figure out if the save was successful or not
		result = db.saveUser(newUser)

		if(result): return newUser.id
		else: return -1

	'''
		Gets a user by id
	'''
	@staticmethod
	def getUser(id):

		#Create Db
		db = DB()
		userJson = db.getUser(id)

		if(userJson is None): return None

		#Convert to User object
		userObject = User()
		userObject.setFromJson(userJson)

		return userObject


	'''
		Add Vision
	'''
	@staticmethod
	def addVision(userId, text, picture, parentId):

		db = DB()

		#serializing from json is the common use case
		newVision = Vision()
		newVision.setInfo(db.getNextVisionId(), userId, text, picture, parentId, time())

		#save
		result = db.saveVision(newVision)
		return result

	'''
		Get Vision
	'''
	@staticmethod
	def getVision(id):

		#Create Db
		db = DB()
		visionJson = db.getVision(id)

		if(visionJson is None): return None

		#Create to Vision Object
		visionObject = Vision()
		visionObject.setFromJson(visionJson)

		return visionObject


	'''
		Get Main Page Visions
	'''
	@staticmethod
	def getMainPageVisions():

		#Number of max visions to return
		MAX_VISIONS = 100

		#Get from db
		db = DB()
		visionsJson = db.mostRecentVisions(MAX_VISIONS)

		#Create Objects
		return DataApi.__visionObjectsFromJson(visionsJson)


	'''
		Get All Visions for User
	'''
	@staticmethod
	def getVisionsForUser(userId):

		#Get from Db
		db = DB()
		visionsJson = db.getVisionsForUser(userId)

		#Create objects
		return DataApi.__visionObjectsFromJson(visionsJson)


	'''
		Vision Objects From Json	
	'''
	@staticmethod
	def __visionObjectsFromJson(visionsJson):
		
		#Create Vision Objects
		visions = []
		for json in visionsJson:
			v = Vision()
			v.setFromJson(json)
			visions.append(v)

		return visions
