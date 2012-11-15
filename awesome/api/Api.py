
#
# Api.py - This is main API for the app. Acts as controller that verifies,
#          gets, modifies, and sets stuff
#

from data.DataApi import DataApi

from ..util.Verifier import Verifier
from ..util.PasswordEncrypt import PasswordEncrypt
from ..util.Logger import Logger

from FlashMessages import *

class Api:
    '''
        addUser - adds new user if input is OK

        This cleans up the input, verifies it, and creates the user if it can.
        If not, we return an error message.

        Returns: (newUserId or None, errorMessage or "" if user created)
    '''
    @staticmethod
    def addUser(firstName, lastName, email, passwordText):
        firstName = firstName.strip()
        lastName = lastName.strip()
        email = email.strip().lower()
        passwordText = passwordText.strip()

        errorMsg = ""

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
        # TODO: NEED TO CHECK EMAIL EXISTS
        elif len(passwordText) <= 0:
            errorMsg = RegisterError.PASSWORD_REQUIRED
        elif not Verifier.passwordValid(passwordText):
            errorMsg = RegisterError.PASSWORD_INVALID

        if errorMsg != "":
            passwordHash = PasswordEncrypt.genHash(passwordText)

            Logger.debug("Name: %s %s, Email: %s, Pass: %s [%s]" % \
                         (firstName, lastName, email,
                          passwordText, passwordHash))

            # Just need to add new user here and login
            userId = DataApi.addUser(firstName, lastName, email, passwordHash)
            if userId  == DataApi.NO_OBJECT_EXISTS_ID:
                return (None, RegisterError.DB_ERROR)
            else:
                return (userId, "")
        else:
            return (None, errorMsg)

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

# $eof
