'''
    Class: Data API

    Main api for data

    Functions:

        Add User
        Get User
        Add Vision 
        Get Vision
        Add Picture
        Get Picture
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
from Picture import Picture
from DB import DB

#For date created
from time import time

class DataApi:

    #Returned when we dont have an object for that id
    NO_OBJECT_EXISTS_ID = -1

    #Returned when the object does not exist
    NO_OBJECT_EXISTS = None

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

        if(result): 
            return newUser.id
        else: 
            return DataApi.NO_OBJECT_EXISTS_ID

    '''
        Gets a user by id
    '''
    @staticmethod
    def getUser(id):

        #Create Db
        db = DB()
        userJson = db.getUser(id)

        #Handle None
        if(userJson is None): 
            return DataApi.NO_OBJECT_EXISTS

        #Convert to User object
        userObject = User()
        userObject.setFromJson(userJson)

        return userObject

    '''
        Gets a user by email address
    '''
    @staticmethod
    def getUserFromEmail(email):
        
        db = DB()
        userJson = db.getUserFromEmail(email)

        #Handle No User
        if(userJson is None): 
            return DataApi.NO_OBJECT_EXISTS

        #Convert to user Object
        userObject = User()
        userObject.setFromJson(userJson)

        return userObject


    '''
        Add Vision
    '''
    @staticmethod
    def addVision(userId, text, pictureId, parentId):

        db = DB()

        #serializing from json is the common use case
        newVision = Vision()
        newVision.setInfo(db.getNextVisionId(), userId, text, pictureId, parentId, time())

        #save
        result = db.saveVision(newVision)
        
        if(result):
            return newVision.id
        else:
            return DataApi.NO_OBJECT_EXISTS_ID
            
    '''
        Repost Vision

    '''
    @staticmethod
    def repostVision(userId, visionId):

        db = DB()
        originalVision = DataApi.getVision(visionId)

        #check to make sure visionId was a valid id
        #if not, return error
        if originalVision is None:
            return DataApi.NO_OBJECT_EXISTS_ID

        #Set the text, userId and parentid
        text = originalVision.text
        pictureId = originalVision.pictureId
        parentId = originalVision.id

        return DataApi.addVision(userId, text, pictureId, parentId)

    '''
        Get Vision
    '''
    @staticmethod
    def getVision(id):

        #Create Db
        db = DB()
        visionJson = db.getVision(id)

        #Handle None
        if(visionJson is None): 
            return DataApi.NO_OBJECT_EXISTS

        #Create to Vision Object
        visionObject = Vision()
        visionObject.setFromJson(visionJson)

        #Get and set the picture object
        picture = DataApi.getPicture(visionObject.pictureId)
        visionObject.setPicture(picture)

        return visionObject

    '''
        Add Picture
    '''
    @staticmethod
    def addPicture(url, filename):

        db = DB()

        #Create Object
        newPicture = Picture()
        newPicture.setInfo(db.getNextPictureId(), url, filename)

        #save
        result = db.savePicture(newPicture)

        if(result):
            return newPicture.id
        else:
            return DataApi.NO_OBJECT_EXISTS_ID


    '''
        Get Picture
    '''
    @staticmethod
    def getPicture(id):

        #Create the db
        db = DB()
        pictureJson = db.getPicture(id)

        #handle None
        if(pictureJson is None): 
            return DataApi.NO_OBJECT_EXISTS

        #Create Picture Object
        pictureObject = Picture()
        pictureObject.setFromJson(pictureJson)

        return pictureObject


    '''
        Get Main Page Visions
    '''
    @staticmethod
    def getMainPageVisions():

        #Number of max visions to return
        MAX_VISIONS = 100

        #Get vision ids from db
        db = DB()
        visionIds = db.mostRecentVisionIds(MAX_VISIONS)

        return DataApi.__visionObjectsFromIds(visionIds)

    '''
        Get All Visions for User
    '''
    @staticmethod
    def getVisionsForUser(userId):

        #Get from Db
        db = DB()
        visionIds = db.getVisionIdsForUser(userId)

        #Create objects
        return DataApi.__visionObjectsFromIds(visionIds)


    '''
        Vision Objects From Json    
    '''
    @staticmethod
    def __visionObjectsFromIds(visionIds):
        
        #Get Visions
        visions = []
        for visionId in visionIds:
            visions.append(DataApi.getVision(visionId))
        
        return visions
