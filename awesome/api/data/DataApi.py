from . import DB
from sqlalchemy.sql import desc
from DbSchema import *
from awesome.util.Logger import Logger
import random

class DataApi:
    '''The interface to actual DB storage
    
    This should assume input is verified and perform minimum operations for
    creating, modifying, deleting, etc. data in the DB.

    One of details in implementation is that wheneve we alter a users vision
    list, we need to keep the VisionListModel consistent.
    '''

    #Returned when we dont have an object for that id
    NO_OBJECT_EXISTS_ID = -1

    #Returned when the object does not exist
    NO_OBJECT_EXISTS = None

    # 
    # User methods
    # These functions return User Model or None if it is not a valid ID
    #

    @staticmethod
    def getUserById(userId):
        user = UserModel.query.filter_by(id=userId).first()
        return user if None != user else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def getUserByEmail(email):
        user = UserModel.query.filter_by(email=email).first()
        return user if None != user else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def setUserName(userId, firstName, lastName):
        user = DataApi.getUserById(userId)
        if None != user:
            change = False
            if user.firstName != firstName:
                user.firstName = firstName
                change = True
            if user.lastName != lastName:
                user.lastName = lastName
                change = True

            if change == True:
                DB.session.add(user)
                DB.session.commit()
                return True
        return False

    @staticmethod
    def setUserEmail(userId, email):
        user = DataApi.getUserById(userId)
        userByEmail = DataApi.getUserByEmail(email)

        # we should find the user, and there shouldn't be another user with
        # the email address they want to use
        if None != user and None == userByEmail:
            user.email = email
            DB.session.add(user)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def setUserDescription(userId, desc):
        user = DataApi.getUserById(userId)

        if None != user and user.description != desc:
            user.description = desc
            DB.session.add(user)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def setUserVisionPrivacy(userId, visionPrivacy):
        user = DataApi.getUserById(userId)

        if None != user and user.visionPrivacy != visionPrivacy:
            user.visionPrivacy = visionPrivacy
            DB.session.add(user)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def setUserPasswordHash(userId, passwordHash):
        user = DataApi.getUserById(userId)
        if None != user:
            if user.passwordHash != passwordHash:
                user.passwordHash = passwordHash
                DB.session.add(user)
                DB.session.commit()
                return True
        return False

    @staticmethod
    def setProfilePicture(userId, url):
        user = DataApi.getUserById(userId)
        if None != user:
            if user.picture != url:
                user.picture = url
                DB.session.add(user)
                DB.session.commit()
                return True
        return False

    @staticmethod
    def addUser(firstName, lastName, email, passwordHash):
        # new UserModel
        user = UserModel(firstName, lastName, email, passwordHash)
        DB.session.add(user)
        DB.session.flush() # so user id is valid

        # new VisionListModel
        visionList = VisionListModel(user.id)
        DB.session.add(visionList)

        DB.session.commit()
        return user.id

    @staticmethod
    def getUsersFromIds(userIds):
        if len(userIds) > 0:
            return UserModel.query \
                        .filter(UserModel.id.in_(userIds)) \
                        .all()
        return []

    #
    # Returns the Vision List (Database) Model
    #

    @staticmethod
    def getVisionListModelForUser(userId):
        visionList = VisionListModel.query.filter_by(userId=userId).first()
        return visionList if None != visionList else DataApi.NO_OBJECT_EXISTS

    #
    #   Returns the array of vision ids owned by the user
    #
    @staticmethod
    def getVisionIdListForUser(userId):
        
        visionListModel = DataApi.getVisionListModelForUser(userId)
        
        if visionListModel != None:
            return visionListModel.getVisionIdList() 
        else:
            return DataApi.NO_OBJECT_EXISTS


    # 
    # Vision methods
    #

    @staticmethod
    def getVision(visionId):
        vision = VisionModel.query.filter_by(id=visionId).first()
        return vision if None != vision else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def visionHasComments(visionId):
        comment = VisionCommentModel.query.filter_by(visionId=visionId) \
                                          .filter_by(removed=False).first()
        return True if None != comment else False

    @staticmethod
    def editVision(visionId, text, privacy):
        vision = DataApi.getVision(visionId)
        if DataApi.NO_OBJECT_EXISTS == vision:
            return False
        change = False
        if text != vision.text:
            vision.text = text
            change = True
        if privacy != vision.privacy:
            vision.privacy = privacy
            change = True
        if change:
            DB.session.add(vision)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def addVision(userId, text, pictureId, parentId, rootId, privacy):
        # get vision list
        visionListModel = DataApi.getVisionListModelForUser(userId)
        assert DataApi.NO_OBJECT_EXISTS != visionListModel, "No vision list"

        vision = VisionModel(userId, text, pictureId, parentId, rootId, privacy)
        DB.session.add(vision)
        DB.session.flush() # flush so vision.id is valid

        # if rootId == 0, root really should be self
        if rootId == 0:
            vision.rootId = vision.id
            DB.session.add(vision)

        # now add to vision list
        visionIds = visionListModel.getVisionIdList()
        visionIds.insert(0, vision.id)
        visionListModel.setVisionIdList(visionIds)
        DB.session.add(visionListModel)

        DB.session.commit()

        assert vision.rootId != 0, "Root ID should never be zero"

        return vision.id

    @staticmethod
    def repostVision(userId, visionId):
        vision = DataApi.getVision(visionId)
        if DataApi.NO_OBJECT_EXISTS == vision:
            return DataApi.NO_OBJECT_EXISTS_ID
        return DataApi.addVision(userId,
                                 vision.text,
                                 vision.pictureId,
                                 vision.id,
                                 vision.rootId,
                                 # TODO: use user default for this later
                                 VisionPrivacy.PUBLIC)
    
    @staticmethod
    def getMainPageVisions():
        return VisionModel.query.filter_by(parentId=0) \
                                .filter_by(privacy=VisionPrivacy.PUBLIC) \
                                .filter_by(removed=False) \
                                .order_by(VisionModel.id.desc()) \
                                .limit(100)

    @staticmethod
    def getVisionsForUser(userId, targetUserId):
        visionListModel = DataApi.getVisionListModelForUser(targetUserId)
        assert DataApi.NO_OBJECT_EXISTS != visionListModel, "No vision list"
        visionIds = visionListModel.getVisionIdList()
        visionModels = []
        if len(visionIds) > 0:
            all_visions = VisionModel.query \
                                     .filter_by(userId=targetUserId) \
                                     .filter_by(removed=False) \
                                     .filter(VisionModel.id.in_(visionIds)) \
                                     .all()

            # hash from visionId to vision
            idToVision = dict([(vision.id, vision) for vision in all_visions])

            visionModels = [idToVision[visionId] for visionId in visionIds]
        return visionModels


    @staticmethod
    def moveUserVision(userId, visionId, srcIndex, destIndex):
        visionListModel = DataApi.getVisionListModelForUser(userId)
        if DataApi.NO_OBJECT_EXISTS == visionListModel:
            return False
        
        visionIds = visionListModel.getVisionIdList()
        length = len(visionIds)

        if srcIndex < 0 or srcIndex >= length or \
           destIndex < 0 or destIndex >= length or \
           visionId != visionIds[srcIndex]:
            return False

        moveId = visionIds.pop(srcIndex)
        visionIds.insert(destIndex, moveId)

        visionListModel.setVisionIdList(visionIds)
        DB.session.add(visionListModel)
        DB.session.commit()
        return True

    @staticmethod
    def deleteUserVision(userId, visionId):
        vision = DataApi.getVision(visionId)
        visionListModel = DataApi.getVisionListModelForUser(userId)
        visionIds = visionListModel.getVisionIdList()

        if vision.userId != userId:
            return False
        if not (visionId in visionIds):
            return False

        # mark the vision as removed
        vision.removed = True
        DB.session.add(vision)

        # now remove from vision list
        visionIds.remove(visionId)
        visionListModel.setVisionIdList(visionIds)
        DB.session.add(visionListModel)

        DB.session.commit()
        return True

    # 
    # Vision Comment methods
    #
    @staticmethod
    def addVisionComment(visionId, authorId, text):
        vision = DataApi.getVision(visionId)
        if vision == DataApi.NO_OBJECT_EXISTS:
            return DataApi.NO_OBJECT_EXISTS

        comment = VisionCommentModel(visionId, authorId, text)
        DB.session.add(comment)
        DB.session.commit()
        return comment

    @staticmethod
    def getVisionComments(visionId, maxComments):
        assert maxComments > 0 and maxComments < 1000, \
               "Invalid max comments value"
        comments = VisionCommentModel.query \
                                     .filter_by(removed=False) \
                                     .filter_by(visionId=visionId) \
                                     .order_by(VisionCommentModel.id.desc()) \
                                     .limit(maxComments)

        # reverse order since we retried them in decreasing id order
        return [comment for comment in reversed([c for c in comments])]

    # 
    # Picture methods
    #

    @staticmethod
    def getPicture(pictureId):
        picture = PictureModel.query.filter_by(id=pictureId).first()
        return picture if None != picture else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def getPicturesFromIds(pictureIds):
        if len(pictureIds) > 0:
            return PictureModel.query \
                            .filter_by(removed=False) \
                            .filter(PictureModel.id.in_(pictureIds)) \
                            .all()
        return []

    @staticmethod
    def addPicture(userId, original, uploaded, s3Bucket,
                           origKey, origWidth, origHeight,
                           largeKey, largeWidth, largeHeight,
                           mediumKey, mediumWidth, mediumHeight,
                           smallKey, smallWidth, smallHeight):
        # new PictureModel
        picture = PictureModel(userId, original, uploaded, s3Bucket,
                                origKey, origWidth, origHeight,
                                largeKey, largeWidth, largeHeight,
                                mediumKey, mediumWidth, mediumHeight,
                                smallKey, smallWidth, smallHeight)
        DB.session.add(picture)
        DB.session.commit()
        return picture.id

    #Get a random vision for the user
    #Returns a vision dictionary with an embedded picture dictionary
    @staticmethod
    def getRandomVision(userId):
        visionIdList = DataApi.getVisionIdListForUser(userId)
        randomId = random.choice(visionIdList)
        
        visionModel = DataApi.getVision(randomId)
        vision = visionModel.__dict__

        pictureModel = DataApi.getPicture(visionModel.pictureId)
        picture = pictureModel.__dict__

        #Set Picture
        vision['picture'] = picture

        return vision

    #Get a random vision per user

    @staticmethod
    def getUsersAndRandomVision():

        #TODO: Filter by Timezone
        #TODO: get SOME
        users = UserModel.query.all()

        userInfo = []
        #Choose a random vision for each user
        for user in users:
            vision = DataApi.getRandomVision(user.id)
            userInfo.append([user, vision])

        return userInfo

      

# $eof
