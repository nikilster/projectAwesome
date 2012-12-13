from data.DataApi import DataApi

from Vision import Vision
from VisionList import VisionList
from VisionComment import VisionComment
from FlashMessages import *
from S3Util import ImageFilePreview, ImageUrlUpload, S3Vision, ProfilePicture

from ..util.Verifier import Verifier
from ..util.PasswordEncrypt import PasswordEncrypt
from ..util.Logger import Logger


# TMP STUFF
from data.DbSchema import VisionPrivacy
# for now randomly generated privacy
# TODO: actually get from front-end later
import random
def getPrivacy():
    if random.randint(0,1) == 0:
        return VisionPrivacy.SHAREABLE
    return VisionPrivacy.PUBLIC
## /end TMP STUFF


class User:
    '''For fetching/creating users and getting/setting user-related values.

    *** IMPORTANT NOTE ***
    All methods on visions which affect the user's vision list order should
    be implemented here. This is because currently the Vision and VisionList
    classes do not know anything about a user's vision list order.
    '''

    #
    # Static user get methods
    #

    @staticmethod
    def getById(userId):
        '''Get user by user id or None '''
        model = DataApi.getUserById(userId)
        if DataApi.NO_OBJECT_EXISTS == model:
            return None
        return User(model)

    @staticmethod
    def getByEmail(email):
        '''Get user by email or None'''
        model = DataApi.getUserByEmail(email)
        if DataApi.NO_OBJECT_EXISTS == model:
            return None
        return User(model)

    @staticmethod
    def getByLogin(email, passwordText):
        '''Get user with login information.

        Returns (User or None, error_msg if first is None)
        '''
        email = email.strip().lower()
        passwordText = passwordText.strip()

        errorMsg = None

        user = User.getByEmail(email)

        if len(email) <= 0:
            errorMsg = LoginError.EMAIL_REQUIRED
        elif None == user:
            errorMsg = LoginError.EMAIL_NOT_FOUND
        elif len(passwordText) <= 0:
            errorMsg = LoginError.PASSWORD_REQUIRED
        elif not PasswordEncrypt.verifyPassword(passwordText,
                                                user.passwordHash()):
            errorMsg = LoginError.PASSWORD_INVALID
        else:
            return (user, None)
        assert errorMsg != None, "Error msg should exist"
        return (None, errorMsg)

    @staticmethod
    def registerNewUser(firstName, lastName, email, passwordText):
        '''Registers and returns new user
        
        Returns (User if successful or None, error_msg if not successful)
        '''
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
            user = User.getByEmail(email)
            if user:
                errorMsg = RegisterError.EMAIL_TAKEN

        if errorMsg == None:
            passwordHash = PasswordEncrypt.genHash(passwordText)

            Logger.debug("Name: %s %s, Email: %s, Pass: %s [%s]" % \
                         (firstName, lastName, email,
                          passwordText, passwordHash))

            # Just need to add new user here and login
            userId = DataApi.addUser(firstName, lastName, email, passwordHash)

            user = User.getById(userId)
            if user:
                return (user, None)
            else:
                return (None, RegisterError.DB_ERROR)
        else:
            return (None, errorMsg)

    #
    # Getters
    #
    def id(self):
        return self._model.id
    def firstName(self):
        return self._model.firstName
    def lastName(self):
        return self._model.lastName
    def fullName(self):
        return self._model.fullName
    def passwordHash(self):
        return self._model.passwordHash
    def email(self):
        return self._model.email
    def emailConfirmed(self):
        return self._model.emailConfirmed
    def picture(self):
        return self._model.picture
    def description(self):
        return self._model.description
    def userPrivacy(self):
        return self._model.userPrivacy
    def visionPrivacy(self):
        return self._model.visionPrivacy

    def toDictionary(self):
        '''Translate to object when we want to package together JSON'''
        return {'id' : self.id(),
                'firstName' : self.firstName(),
                'lastName' : self.lastName(),
                'picture' : self.picture(),
                'description' : self.description(),
                'visionPrivacy' : self.visionPrivacy(),
               }

    #
    # Setters (note: these write to database)
    #
    def setInfo(self, firstName, lastName, email):
        '''Returns True if something changed, else False'''
        change = False
        if Verifier.nameValid(firstName) and \
           Verifier.nameValid(lastName) and \
           Verifier.emailValid(email):
            change |= DataApi.setUserName(self.id(), firstName, lastName)
            change |= DataApi.setUserEmail(self.id(), email)
        return change

    def setDescription(self, description):
        '''Returns True if description changed, else False'''
        return DataApi.setUserDescription(self.id(), description.strip())

    def setProfilePicture(file):
        '''Sets profile picture from file input stream

        Returns URL on success, else None
        '''
        image = ProfilePicture(file)
        url = None
        if file and image.isImage():
            url = image.uploadToS3(userId)
            if url != None:
                if True == DataApi.setProfilePicture(self.id(), url):
                    return url
        return None

    #
    # Methods for dealing with a user's vision
    #
    # *** ALWAYS edit user visions through user first. We want to    ***
    #     make sure the users vision list order gets updated also.
    #

    def previewImage(self, file):
        '''Upload file input to S3 for file preview

        Return URL of preview image on success, else None.
     
        *** IMPORTANT NOTE ***
        The preview file on S3 is unique per user. Files previewed at
        same time in different tabs will overwrite each other.
        '''
        image = ImageFilePreview(file)
        url = None
        if file and image.isImage():
            url = image.uploadForPreview(self.id())
        return url

    def addVision(self, imageUrl, text, isUploaded):
        '''Creates new vision
        
        Returns (Vision/None, None or error_msg if add vision failed)
        '''
        #TODO: Save page title and page URL?

        if imageUrl == "":
            return [None, "No image"]
        imageUpload = ImageUrlUpload(imageUrl)
        s3Vision = imageUpload.saveAsVisionImage(self.id())

        if None == s3Vision:
            return [None, "Invalid image"]
            
        pictureId = DataApi.addPicture(self.id(),
                                       imageUrl, isUploaded,
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
            return [None, "Error saving picture"]

        parentId = 0
        rootId = 0
        # TODO: use real privacy later
        visionId = DataApi.addVision(self.id(), text, pictureId,
                                     parentId, rootId, getPrivacy())

        if visionId == DataApi.NO_OBJECT_EXISTS_ID:
            return [None, "Error creating vision"]

        vision = Vision.getById(visionId)
        if vision:
            return [vision, "Saved Vision!"]
        else:
            return [None, "Error retrieving vision"]

    def repostVision(self, visionId):
        '''Repost a vision and return new vision if successful, else None'''
        newVisionId = DataApi.repostVision(self.id(), visionId)
        if DataApi.NO_OBJECT_EXISTS_ID == newVisionId:
            return None
        vision = Vision.getById(newVisionId)
        return vision

    def repostVisionList(self, visionIds):
        '''Convenience function that loops over self.repostVision()'''
        for visionId in reversed(visionIds):
            self.repostVision(visionId)

    def moveVision(self, visionId, srcIndex, destIndex):
        '''Returns True if move worked, False if it failed'''
        return DataApi.moveUserVision(self.id(), visionId, srcIndex, destIndex)

    def deleteVision(self, visionId):
        '''Returns True if delete worked, False if it failed'''
        return DataApi.deleteUserVision(self.id(), visionId)

    def randomVision(self):
        '''Returns random vision or None if vision list is empty'''
        randomModel = DataApi.getRandomUserVision(self.id())
        if DataApi.NO_OBJECT_EXISTS == randomModel:
            return None
        else:
            return Vision._getByModel(randomModel)

    #
    # User actions
    #

    def commentOnVision(self, visionId, text):
        '''Returns comment if successful, else returns None'''
        text = text.strip()
        if len(text) > 0:
            commentModel = DataApi.addVisionComment(visionId, self.id(), text)
            if DataApi.NO_OBJECT_EXISTS == commentModel:
                return None
            else:
                return VisionComment._getByModel(commentModel)
        else:
            return None

    #
    # Private methods
    #

    def __init__(self, model):
        '''IMPORTANT: Do NOT call this. Use static methods above'''
        assert model, "User model is invalid"
        self._model = model

# $eof
