'''
 Api.py
 
 This is main API for the app. Acts as controller that verifies,
    gets, modifies, and sets stuff
'''

from data.DataApi import DataApi

from ..util.Verifier import Verifier
from ..util.PasswordEncrypt import PasswordEncrypt
from ..util.Logger import Logger

#TODO: Why does (the ..) this work?
from ..Constant import Constant

from FlashMessages import *

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

        user = DataApi.getUserFromEmail(email)

        if len(email) <= 0:
            errorMsg = LoginError.EMAIL_REQUIRED
        elif DataApi.NO_OBJECT_EXISTS == user:
            errorMsg = LoginError.EMAIL_NOT_FOUND
        elif len(passwordText) <= 0:
            errorMsg = LoginError.PASSWORD_REQUIRED
        elif not PasswordEncrypt.verifyPassword(passwordText, user.password):
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
            user = DataApi.getUserFromEmail(email)
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
    def getUserById(userId):
        return DataApi.getUser(userId)

    #
    # Vision-related API
    #
    @staticmethod
    def getMainPageVisions():
        return DataApi.getMainPageVisions()

    @staticmethod
    def getVisionsForUser(userId):
        return DataApi.getVisionsForUser(userId)

    @staticmethod
    def moveUserVision(userId, visionId, srcIndex, destIndex):
        return DataApi.moveUserVision(userId, visionId, srcIndex, destIndex)

    '''
        Save (Right now from the bookmarklet)
    '''
    @staticmethod
    def saveVision(userId, imageUrl, text, pageUrl):

        #To Do Validate
        url = imageUrl
        filename = "name on server"
        pictureId = DataApi.addPicture(url, filename)

        if pictureId == DataApi.NO_OBJECT_EXISTS_ID:
            return [Constant.INVALID_OBJECT_ID,"Error saving picture"]

        parentId = 0
        visionId = DataApi.addVision(userId, text, pictureId, parentId)

        if visionId == DataApi.NO_OBJECT_EXISTS_ID:
            return [Constant.INVALID_OBJECT_ID,"Error saving picture"]

        return [visionId, "Saved Vision!"]
# $eof
