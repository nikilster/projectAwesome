'''
	DB

	Provides functins to access the data in the database

	DONE:
	Save User
	Get User
	Save Vision
	Get Vision

	TODO:
'''
import redis

class DB:

	#From https://github.com/andymccurdy/redis-py#getting-started
	HOST = 'localhost'
	PORT = 6379
	DB_ID = 0

	#Prefixes for the 
	#different setsz (uses the id  after the color)
	USER_PREFIX = "user:"
	VISION_PREFIX = "vision:"
	USER_VISION_SET_PREFIX = "visionsSetForUser:"

	#Increment Keys
	USER_NEXT_ID_KEY = "global:nextUserId"
	VISION_NEXT_ID_KEY = "global:nextVisionId"

	#set up redis
	def __init__(self):
		#from https://github.com/andymccurdy/redis-py#getting-started
		self.r = redis.StrictRedis(host=DB.HOST, port=DB.PORT, db=DB.DB_ID)

	#Save the user to db
	def saveUser(self, newUser):
		userKey = self.__getUserKey(newUser.id)
		return self.r.set(userKey, newUser.toJson())

	#Get the user from the db
	def getUser(self, userId):
		userKey = self.__getUserKey(userId)
		return self.r.get(userKey)


	#Save the vision to the db
	def saveVision(self, newVision):

		#Save to the Main Vision Set
		visionKey = self.__getVisionKey(newVision.id)
		save1 = self.r.set(visionKey, newVision.toJson())

		#Save to the User Vision Set
		#This is actually a set
		userVisionSetKey = self.__getUserVisionSetKey(newVision.userId)
		visionId = self.__cleanInt(newVision.id)

		#save 
		save2 = self.r.sadd(userVisionSetKey, visionId)

		return save1 and save2

	#Get Vision
	def getVision(self, visionId):
		visionKey = self.__getVisionKey(visionId)
		return self.r.get(visionKey)

	#Get Visions for User
	def getVisionsForUser(self, userId):
		
		#Get User Vision Set
		userVisionSetKey = self.__getUserVisionSetKey(userId)
		visionIds = self.r.smembers(userVisionSetKey)

		#Get the visions
		visions = []
		for id in visionIds:
			visions.append(self.getVision(id))

		return visions

	#Get the maxCount most recent visions
	def mostRecentVisions(self, maxCount):

		#Return the min of (existing, maxtoreturn <- passed by caller)
		numTotalVisions = self.__getNumVisions()
		numVisionsToReturn = min(numTotalVisions, maxCount)

		#non inclusive
		finalRangeIndex = numTotalVisions - numVisionsToReturn

		#Get Visions
		visions = []
		for visionId in range(numTotalVisions, finalRangeIndex, -1):
			visions.append(self.getVision(visionId))

		return visions

	#Gets the next user id from the global counter in the database
	def getNextUserId(self):
		return self.r.incr(DB.USER_NEXT_ID_KEY)

	#Gets the next vision id from the global counter in the database
	def getNextVisionId(self):
		return self.r.incr(DB.VISION_NEXT_ID_KEY)
	
	#TODO: Check this
	#Assume contiguous
	def __getNumVisions(self):
		return int(self.r.get(DB.VISION_NEXT_ID_KEY)) - 1

	#make sure that the argument is a numeric string
	#returns a string that is guaranteed to be an integer
	def __cleanInt(self, number):
		return str(int(number))

	#Function which returns the correct format of the string to index into
	#the main user set 
	def __getUserKey(self, userId):
		return DB.USER_PREFIX + self.__cleanInt(userId)

	#Function which returns the correct format of the string to index into
	#the vision set
	def __getVisionKey(self, visionId):
		return DB.VISION_PREFIX + self.__cleanInt(visionId)

	#Function which returns the correct format of the string to index into
	#the user vision
	def __getUserVisionSetKey(self, userId):
		return DB.USER_VISION_SET_PREFIX + self.__cleanInt(userId)
