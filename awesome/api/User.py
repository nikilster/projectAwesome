from data.DataApi import DataApi

from Follow import Follow
from Vision import Vision
from VisionList import VisionList
from VisionComment import VisionComment
from VisionCommentList import VisionCommentList
from Privacy import VisionPrivacy
from FlashMessages import *
from S3Util import ImageFilePreview, ImageUrlUpload, S3Vision, ProfilePicture

from ..util.Verifier import Verifier
from ..util.PasswordEncrypt import PasswordEncrypt
from ..util.Logger import Logger


class User:
    '''For fetching/creating users and getting/setting user-related values.

    *** IMPORTANT NOTE ***
    All methods on visions which affect the user's vision list order should
    be implemented here. This is because currently the Vision and VisionList
    classes do not know anything about a user's vision list order.
    '''

    #
    # Constants, enums
    #
    class Key:
        ''' For dictionary use'''
        ID = 'id'
        FIRST_NAME = 'firstName'
        LAST_NAME = 'lastName'
        FULL_NAME = 'fullName'
        PICTURE = 'picture'
        DESCRIPTION = 'description'
        VISION_PRIVACY = 'visionPrivacy'
        # If using Option.FOLLOW_COUNT
        FOLLOW_COUNT = 'followCount'
        FOLLOWER_COUNT = 'followerCount'
        # If using Option.FOLLOWING
        FOLLOW = 'follow'
        # Only if calling toDictionaryFull.
        EMAIL = 'email'

    class Options:
        '''Extra options to pass into toDictionary()'''
        FOLLOW_COUNTS = 0       # Add follow and follower counts into dict
        FOLLOWING = 1           # If this user is following 'user' parameter


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
        return User._getByLogin(email, passwordText)

    @staticmethod
    def registerNewUser(firstName, lastName, email, passwordText):
        '''Registers and returns new user
        
        Returns (User if successful or None, error_msg if not successful)
        '''
        return User._registerNewUser(firstName, lastName, email, passwordText)

    @staticmethod
    def getByUserIds(userIds):
        '''Gets a list of Users from a list of userIds'''
        models = DataApi.getUsersFromIds(userIds)
        return [User(model) for model in models]

    @staticmethod
    def getAllUsers():
        '''Gets a list of Users from a list of userIds'''
        models = DataApi.getAllUsers()
        return [User(model) for model in models]


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
    def model(self):
        ''' Get internal DB model'''
        return self._model

    #
    # Convenience methods
    #
    def sameUser(self, user):
        '''Returns T if user is same is user passed as parameter.'''
        return self.id() == user.id()

    def visionDefaultIsPublic(self):
        return VisionPrivacy.PUBLIC == self.visionPrivacy()

    def visionList(self, inquiringUser):
        '''Gets VisionList with respect to privacy of inquiringUser, or None'''
        return VisionList.getUserVisions(inquiringUser, self)

    def toDictionary(self, options=[], user=None):
        '''Translate to object when we want to package together JSON'''
        obj =  { User.Key.ID                : self.id(),
                 User.Key.FIRST_NAME        : self.firstName(),
                 User.Key.LAST_NAME         : self.lastName(),
                 User.Key.FULL_NAME         : self.fullName(),
                 User.Key.PICTURE           : self.picture(),
                 User.Key.DESCRIPTION       : self.description(),
                 User.Key.VISION_PRIVACY    : self.visionPrivacy(),
               }
        if User.Options.FOLLOW_COUNTS in options:
            obj[User.Key.FOLLOW_COUNT] = self.followCount()
            obj[User.Key.FOLLOWER_COUNT] = self.followerCount()
        if User.Options.FOLLOWING:
            if user:
                if user.id() != self.id():
                    obj[User.Key.FOLLOW] = user.follows(self)
        return obj

    def toDictionaryFull(self):
        '''Like toDictionary() but with all user information.
        
        Avoid using when you don't want private info to leak (e.g. email).'''
        obj = self.toDictionary()
        obj[User.Key.EMAIL] = self.email()
        return obj


    def isAdmin(self):
        '''Quick way to differentiate between admin users for now'''
        email = self.email()
        if email == "alex.shye@gmail.com" or \
           email == "nikil@stanford.edu":
            return True
        return False

    #
    # Setters (note: these write to database)
    #
    def setInfo(self, firstName, lastName, email, visionPrivacy):
        '''Returns True if something changed, else False'''
        change = False
        if Verifier.nameValid(firstName) and \
           Verifier.nameValid(lastName) and \
           Verifier.emailValid(email):
            change |= DataApi.setUserName(self.model(), firstName, lastName)
            change |= DataApi.setUserEmail(self.model(), email)
            change |= DataApi.setUserVisionPrivacy(self.model(), visionPrivacy)
        return change

    def setDescription(self, description):
        '''Returns True if description changed, else False'''
        return DataApi.setUserDescription(self.model(), description.strip())

    def setProfilePicture(self, file):
        '''Sets profile picture from file input stream

        Returns URL on success, else None
        '''
        image = ProfilePicture(file)
        url = None
        if file and image.isImage():
            url = image.uploadToS3(self.id())
            if url != None:
                if True == DataApi.setProfilePicture(self.model(), url):
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

    def addVision(self, imageUrl, text, isUploaded, isPublic):
        '''Creates new vision
        
        TODO: What does isUploaded mean?
        
        Returns (Vision/None, None or error_msg if add vision failed)
        '''
        #TODO: Save page title and page URL?

        if imageUrl == "":
            return [None, "No image"]
        if len(text.strip()) <= 0:
            return [None, "No text"]

        pictureId, errorMsg = self._processAndUploadImageUrl(imageUrl, isUploaded)
        if pictureId == None:
            return [None, "Error saving picture"]

        privacy = VisionPrivacy.PUBLIC
        if not isPublic:
            privacy = VisionPrivacy.PRIVATE

        visionId = DataApi.addVision(self.model(), text, pictureId,
                                     0, 0, privacy)
        if visionId == DataApi.NO_OBJECT_EXISTS_ID:
            return [None, "Error creating vision"]
        vision = Vision.getById(visionId, self)
        if vision:
            return [vision, "Saved Vision!"]
        else:
            return [None, "Error retrieving vision"]

    def repostVision(self, vision):
        '''Repost a vision and return new vision if successful, else None'''
        assert vision, "Invalid vision"

        isPublic = self.visionDefaultIsPublic()
        newVisionId = DataApi.repostVision(self.model(),
                                           vision.model(),
                                           isPublic)
        if DataApi.NO_OBJECT_EXISTS_ID != newVisionId:
            newVision = Vision.getById(newVisionId, self)
            if newVision:
                # Only let original user know if this vision is posted
                # publicly
                if isPublic:
                    from ..WorkerJobs import Queue_repostEmail
                    Queue_repostEmail(self.toDictionary(),
                                  vision.toDictionary(),
                                  newVision.toDictionary())
                return newVision
        return None

    def repostVisionList(self, visionIds):
        '''Convenience function that loops over self.repostVision()'''
        for visionId in reversed(visionIds):
            # TODO: Speed up later by grabbing list of visions
            vision = Vision.getById(visionId, self)
            if vision:
                self.repostVision(vision)

    def moveVision(self, visionId, srcIndex, destIndex):
        '''Returns True if move worked, False if it failed'''
        return DataApi.moveUserVision(self.model(), visionId,
                                      srcIndex, destIndex)

    def deleteVision(self, visionId):
        '''Returns True if delete worked, False if it failed'''
        return DataApi.deleteUserVision(self.model(), visionId)

    def randomVision(self):
        '''Returns random vision or None if vision list is empty.
        
        *** IMPORTANT NOTE ***
        Does NOT take privacy into account. This is only used for email for now.
        '''
        visionList = self.visionList(self)
        return visionList.randomVision()

    #
    # User actions
    #

    def commentOnVision(self, visionId, text):
        '''Returns comment if successful, else returns None'''
        from ..WorkerJobs import Queue_commentEmail, \
                                 Queue_commentNotificationEmail

        vision = Vision.getById(visionId, self)
        if vision:
            comment = vision.addComment(self, text)
            if comment:
                # If comment is on someone else's vision, email them
                if vision.userId() != self.id():
                    Queue_commentEmail(self.toDictionary(),
                                       vision.toDictionary(),
                                       comment.toDictionary())
                # send comment notifications for others that have commented
                # that are not the vision user or the author user
                # TODO: figure out better heuristic for how far to go back
                commentList = vision.comments(50)
                userIdSet = set()
                for comment in commentList.comments():
                    if comment.authorId() != self.id() and \
                       comment.authorId() != vision.userId():
                        userIdSet.add(comment.authorId())
                otherCommenters = User.getByUserIds(userIdSet)
                for otherCommenter in otherCommenters:
                    Queue_commentNotificationEmail(
                                       otherCommenter.toDictionaryFull(),
                                       self.toDictionary(),
                                       vision.toDictionary(),
                                       comment.toDictionary())
            return comment
        return None

    #
    # Follow methods
    #
    def follows(self, user):
        '''Returns True if self follows user, else False'''
        Logger.debug("GET FOLLOW: " + str(self.id()) + " " +
                     str(user.id()))
        follow = Follow.get(self, user)
        if follow:
            Logger.debug("FOLLOW: " + str(follow.followerId()) + " " +
                        str(follow.userId()))
        else:
            Logger.debug("NO FOLLOW");
        return follow != None

    def followUser(self, user):
        '''Returns new follow, or None'''
        if self.id() == user.id():
            return None
        followModel = DataApi.addFollow(self.model(), user.model())
        return Follow(followModel)

    def unfollowUser(self, user):
        '''Remove an existing follow'''
        if self.id() == user.id():
            return False
        return DataApi.removeFollow(self.model(), user.model())

    def followCount(self):
        '''Returns count of number of people this user follows'''
        return Follow.getUserFollowCount(self)

    def followerCount(self):
        '''Returns count of number of people following this user'''
        return Follow.getUserFollowerCount(self)

    def getFollows(self, number=0):
        '''Returns list of users this user follows.
        
        (Optional) use 'number' to limit number of recent follows
        '''
        follows = Follow.getUserFollows(self.model(), number)
        userIds = [follow.userId() for follow in follows]
        return User.getByUserIds(userIds)


    def getFollowers(self, number=0):
        '''Returns list of users this user follows

        (Optional) use 'number' to limit number of recent follows
        '''
        follows = Follow.getUserFollowers(self.model(), number)
        userIds = [follow.followerId() for follow in follows]
        return User.getByUserIds(userIds)

    #
    # Private methods
    #

    def __init__(self, model):
        '''IMPORTANT: Do NOT call this. Use static methods above'''
        assert model, "User model is invalid"
        self._model = model

    @staticmethod
    def _getByLogin(email, passwordText):
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
    def _registerNewUser(firstName, lastName, email, passwordText):
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


    def _processAndUploadImageUrl(self, imageUrl, isUploaded):
        if imageUrl == "":
            return [None, "No image"]
        imageUpload = ImageUrlUpload(imageUrl)
        s3Vision = imageUpload.saveAsVisionImage(self.id())

        if None == s3Vision:
            return [None, "Invalid image"]
            
        pictureId = DataApi.addPicture(self.model(),
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

        return [pictureId, "Success"]

# $eof
