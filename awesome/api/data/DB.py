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
    EMAIL_PREFIX = "email:"     #email -> userId
    VISION_PREFIX = "vision:"
    PICTURE_PREFIX = "picture:"
    USER_VISION_LIST_PREFIX = "visionListForUser:"


    #Increment Keys
    USER_NEXT_ID_KEY = "global:nextUserId"
    VISION_NEXT_ID_KEY = "global:nextVisionId"
    PICTURE_NEXT_ID_KEY = "global:nextPictureId"

    #set up redis
    def __init__(self):
        #from https://github.com/andymccurdy/redis-py#getting-started
        self.r = redis.StrictRedis(host=DB.HOST, port=DB.PORT, db=DB.DB_ID)

    #Save the user to db
    def saveUser(self, newUser):
        
        #Save user to the user id set
        userKey = self.__getUserKey(newUser.id)
        save1 = self.r.set(userKey, newUser.toJson())

        #Save the user to the Email -> userId mapping
        emailKey = self.__getEmailKey(newUser.email)
        userId = self.__cleanInt(newUser.id)
        save2 = self.r.set(emailKey, userId)

        #Return if true if both are successful
        return save1 and save2

    #Get the user from the db
    def getUser(self, userId):
        userKey = self.__getUserKey(userId)
        return self.r.get(userKey)


    #Get the user by email
    def getUserFromEmail(self, email):
        emailKey = self.__getEmailKey(email)
        userId = self.r.get(emailKey)

        #If the user exists
        if userId is not None:
            return self.getUser(userId)
        else:
            return None

    #Save the vision to the db
    def saveVision(self, newVision):

        #Save to the Main Vision Set
        visionKey = self.__getVisionKey(newVision.id)
        save1 = self.r.set(visionKey, newVision.toJson())

        #Save to the User Vision list
        userVisionListKey = self.__getUserVisionListKey(newVision.userId)
        visionId = self.__cleanInt(newVision.id)
        save2 = self.r.lpush(userVisionListKey, visionId)

        #Return whether both different saves are successful 
        return save1 and save2

    #Get Vision
    def getVision(self, visionId):
        visionKey = self.__getVisionKey(visionId)
        return self.r.get(visionKey)


    #Save the picture to the db
    def savePicture(self, newPicture):
        pictureKey = self.__getPictureKey(newPicture.id)
        return self.r.set(pictureKey, newPicture.toJson())

    #Get the picture from the db
    def getPicture(self, pictureId):
        pictureKey = self.__getPictureKey(pictureId)
        return self.r.get(pictureKey)


    #Get Visions for User
    def getVisionIdsForUser(self, userId):
        
        #Get User Vision Set
        userVisionListKey = self.__getUserVisionListKey(userId)
        visionIds = self.r.lrange(userVisionListKey,
                                  0,
                                  self.r.llen(userVisionListKey) - 1)

        return visionIds

    #Get the ids of the maxCount most recent visions
    def mostRecentVisionIds(self, maxCount):

        #Return the min of (existing, maxtoreturn <- passed by caller)
        numTotalVisions = self.__getNumVisions()
        numVisionsToReturn = min(numTotalVisions, maxCount)

        #non inclusive
        finalRangeIndex = numTotalVisions - numVisionsToReturn

        #Get Vision Ids
        return range(numTotalVisions, finalRangeIndex, -1)


    '''
        Object Id Counters
    '''
    #Gets the next user id from the global counter in the database
    def getNextUserId(self):
        return self.r.incr(DB.USER_NEXT_ID_KEY)

    #Gets the next vision id from the global counter in the database
    def getNextVisionId(self):
        return self.r.incr(DB.VISION_NEXT_ID_KEY)
    
    #Gets the next picture id from the global counter in the database
    def getNextPictureId(self):
        return self.r.incr(DB.PICTURE_NEXT_ID_KEY)



    #TODO: Check this
    #Assume contiguous
    def __getNumVisions(self):
        return int(self.r.get(DB.VISION_NEXT_ID_KEY)) - 1

    #make sure that the argument is a numeric string
    #returns a string that is guaranteed to be an integer
    def __cleanInt(self, number):
        return str(int(number))

    #Clean the email passed in address
    #TODO: do this!
    def __cleanEmail(self, email):
        return str(email)


    '''
        Keys
    '''
    #Function which returns the correct format of the string to index
    #to get the user 
    def __getUserKey(self, userId):
        return DB.USER_PREFIX + self.__cleanInt(userId)

    def __getEmailKey(self, email):
        return DB.EMAIL_PREFIX + self.__cleanEmail(email)

    #Function which returns the correct format of the string to index
    #to get the vision
    def __getVisionKey(self, visionId):
        return DB.VISION_PREFIX + self.__cleanInt(visionId)

    #Function which returns the correct format of the string to index 
    #to get the picture
    def __getPictureKey(self, pictureId):
        return DB.PICTURE_PREFIX + self.__cleanInt(pictureId)

    #Function which returns the correct format of the string to index into
    #the user vision
    def __getUserVisionListKey(self, userId):
        return DB.USER_VISION_LIST_PREFIX + self.__cleanInt(userId)



    #!!!!!!
    def __secretClean(self):
        return self.r.flushdb()
