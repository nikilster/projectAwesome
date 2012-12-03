'''
 Api.py
 
 This is main API for the app. Acts as controller that verifies,
    gets, modifies, and sets stuff
'''

#from data.RedisDataApi import RedisDataApi
from data.DataApi import DataApi

from ..util.Verifier import Verifier
from ..util.PasswordEncrypt import PasswordEncrypt
from ..util.Logger import Logger

#TODO: Why does (the ..) this work?
from ..Constant import Constant

from FlashMessages import *
from S3Util import ImageFilePreview, ImageUrlUpload, S3Vision

class Api:
    '''
        loginUser - verifies input, and returns user if exists

        Returns: (user or None, errorMessage if user is None)
    '''
    @staticmethod
    def loginUser(email, passwordText):
        email = email.strip().lower()
        passwordText = passwordText.strip()

        errorMsg = None

        user = DataApi.getUserByEmail(email)

        if len(email) <= 0:
            errorMsg = LoginError.EMAIL_REQUIRED
        elif DataApi.NO_OBJECT_EXISTS == user:
            errorMsg = LoginError.EMAIL_NOT_FOUND
        elif len(passwordText) <= 0:
            errorMsg = LoginError.PASSWORD_REQUIRED
        elif not PasswordEncrypt.verifyPassword(passwordText,
                                                user.passwordHash):
            errorMsg = LoginError.PASSWORD_INVALID
        else:
            return (user, None)
        assert errorMsg != None, "Error msg should exist"
        return (None, errorMsg)
       

    '''
        registerUser - adds new user if input is OK

        This cleans up the input, verifies it, and creates the user if it can.
        If not, we return an error message.

        Returns: (newUserId or None, errorMessage or "" if user created)
    '''
    @staticmethod
    def registerUser(firstName, lastName, email, passwordText):
        firstName = firstName.strip()
        lastName = lastName.strip()
        email = email.strip().lower()
        passwordText = passwordText.strip()

        errorMsg = None

        if len(firstName) <= 0:
            errorMsg = RegisterError.FIRST_NAME_REQUIRED
        elif not Verifier.nameValid(firstName):
            errorMsg = RegisterError.FIRST_NAME_INVALID
        elif len(lastName) <= 0:
            errorMsg = RegisterError.LAST_NAME_REQUIRED
        elif not Verifier.nameValid(lastName):
            errorMsg = RegisterError.LAST_NAME_INVALID
        elif len(email) <= 0:
            errorMsg = RegisterError.EMAIL_REQUIRED
        elif not Verifier.emailValid(email):
            errorMsg = RegisterError.EMAIL_INVALID
        elif len(passwordText) <= 0:
            errorMsg = RegisterError.PASSWORD_REQUIRED
        elif not Verifier.passwordValid(passwordText):
            errorMsg = RegisterError.PASSWORD_INVALID
        else:
            user = DataApi.getUserByEmail(email)
            if DataApi.NO_OBJECT_EXISTS != user:
                errorMsg = RegisterError.EMAIL_TAKEN

        if errorMsg == None:
            passwordHash = PasswordEncrypt.genHash(passwordText)

            Logger.debug("Name: %s %s, Email: %s, Pass: %s [%s]" % \
                         (firstName, lastName, email,
                          passwordText, passwordHash))

            # Just need to add new user here and login
            userId = DataApi.addUser(firstName, lastName, email, passwordHash)
            if userId != DataApi.NO_OBJECT_EXISTS_ID:
                return (userId, None)
            else:
                return (None, RegisterError.DB_ERROR)
        else:
            return (None, errorMsg)

    @staticmethod
    def repostVisionList(userId, visionIds):
        for visionId in reversed(visionIds):
            Logger.debug("REPOST: " + str(visionId) +  "USER: " + str(userId))
            DataApi.repostVision(userId, visionId)

    @staticmethod
    def repostVision(userId, visionId):
        newVisionId = DataApi.repostVision(userId, visionId)
        if DataApi.NO_OBJECT_EXISTS_ID == newVisionId:
            return None
        newVision = DataApi.getVision(newVisionId)
        if DataApi.NO_OBJECT_EXISTS == newVision:
            return None
        return newVision

    @staticmethod
    def getUserById(userId):
        return DataApi.getUserById(userId)

    #
    # Vision-related API
    #
    @staticmethod
    def getMainPageVisionList():
        data = DataApi.getMainPageVisions()
        visionList = []
        for vision in data:
            visionList.append(vision.toDictionary())
        return visionList

    @staticmethod
    def getUserVisionList(userId):
        data = DataApi.getVisionsForUser(userId)
        visionList = []
        for vision in data:
            visionList.append(vision.toDictionary())
        return visionList

    @staticmethod
    def moveUserVision(userId, visionId, srcIndex, destIndex):
        return DataApi.moveUserVision(userId, visionId, srcIndex, destIndex)

    @staticmethod
    def deleteUserVision(userId, visionId):
        return DataApi.deleteUserVision(userId, visionId)

    '''
        PreviewImage

        return None if couldn't upload, else returns URL of preview image
    '''
    @staticmethod
    def previewImage(userId, file):
        image = ImageFilePreview(file)
        url = None
        if file and image.isImage():
            url = image.uploadForPreview(userId)
        return url

    '''
        Save (Right now from the bookmarklet)

        isUploaded: True of user manually uploaded. False if from URL
    '''
    @staticmethod
    def saveVision(userId, mediaUrl, text, pageUrl, pageTitle, isUploaded):
        #To Do Validate
        #TODO: Save page title
        filename = "name on server"

        if mediaUrl == "":
            return [Constant.INVALID_OBJECT_ID,"No image"]
        imageUpload = ImageUrlUpload(mediaUrl)
        s3Vision = imageUpload.saveAsVisionImage(userId)

        if None == s3Vision:
            return [Constant.INVALID_OBJECT_ID,"Invalid image"]
            
        pictureId = DataApi.addPicture(userId,
                                       mediaUrl, isUploaded,
                                       s3Vision.s3Bucket(),
                                       s3Vision.origKey(),
                                       s3Vision.origWidth(),
                                       s3Vision.origHeight(),
                                       s3Vision.largeKey(),
                                       s3Vision.largeWidth(),
                                       s3Vision.largeHeight(),
                                       s3Vision.mediumKey(),
                                       s3Vision.mediumWidth(),
                                       s3Vision.mediumHeight(),
                                       s3Vision.smallKey(),
                                       s3Vision.smallWidth(),
                                       s3Vision.smallHeight())

        if pictureId == DataApi.NO_OBJECT_EXISTS_ID:
            return [Constant.INVALID_OBJECT_ID,"Error saving picture"]

        parentId = 0
        rootId = 0
        visionId = DataApi.addVision(userId, text, pictureId, parentId, rootId)

        if visionId == DataApi.NO_OBJECT_EXISTS_ID:
            return [Constant.INVALID_OBJECT_ID,"Error saving picture"]

        return [visionId, "Saved Vision!"]

    @staticmethod
    def getVision(visionId):
        return DataApi.getVision(visionId)

# $eof
