from . import DB

from sqlalchemy.sql import desc

from DbSchema import *

from awesome.util.Logger import Logger

class UserRelationship:
    NONE = 0    # either anonymous user, or there is no relationship
    SELF = 1    # user and target user are same person
    SHARED = 2  # target user has shared with user requesting data

def getUserRelationship(userId, targetUserId):
    assert targetUserId != None and targetUserId > 0, "Invalid target user id: %s" % (str(targetUserId))
    assert userId == None or userId > 0, "Invalid user id: %s" % (str(userId))

    # Right now we don't support the mastermind group so you either are your
    # self, or you aren't related.
    if None != userId and userId == targetUserId:
        return UserRelationship.SELF
    return UserRelationship.NONE

class DataApi:
    #Returned when we dont have an object for that id
    NO_OBJECT_EXISTS_ID = -1

    #Returned when the object does not exist
    NO_OBJECT_EXISTS = None

    # 
    # User methods
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
        user = DatapApi.getUserById(userId)
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
    def setUserPasswordHash(userId, passwordHash):
        user = DatapApi.getUserById(userId)
        if None != user:
            if user.passwordHash != passwordHash:
                user.passwordHash = passwordHash
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
        return UserModel.query \
                        .filter(UserModel.id.in_(userIds)) \
                        .all()

    # 
    # Vision List methods
    #

    @staticmethod
    def getVisionListModelForUser(userId):
        visionList = VisionListModel.query.filter_by(userId=userId).first()
        return visionList if None != visionList else DataApi.NO_OBJECT_EXISTS

    # 
    # Vision methods
    #

    @staticmethod
    def getVision(visionId):
        vision = VisionModel.query.filter_by(id=visionId).first()
        return vision if None != vision else DataApi.NO_OBJECT_EXISTS

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

        relationship = getUserRelationship(userId, targetUserId)

        visions = []
        if len(visionIds) > 0:
            all_visions = VisionModel.query \
                                     .filter_by(userId=targetUserId) \
                                     .filter_by(removed=False) \
                                     .filter(VisionModel.id.in_(visionIds)) \
                                     .all()

            # hash from visionId to vision
            idToVision = dict([(vision.id, vision) for vision in all_visions])

            # use hash and relationship to go from visionIds to ordered
            # vision list
            if UserRelationship.NONE == relationship:
                # Only show public visions
                visions = [idToVision[visionId] for visionId in visionIds \
                                if idToVision[visionId].privacy == \
                                    VisionPrivacy.PUBLIC]
            elif UserRelationship.SELF == relationship:
                # Show all visions
                visions = [idToVision[visionId] for visionId in visionIds]
            else:
                assert false, "Invalid user relationship"

        return visions

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
    # Picture methods
    #

    @staticmethod
    def getPicture(pictureId):
        picture = PictureModel.query.filter_by(id=pictureId).first()
        return picture if None != picture else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def getPicturesFromIds(pictureIds):
        return PictureModel.query \
                           .filter_by(removed=False) \
                           .filter(PictureModel.id.in_(pictureIds)) \
                           .all()

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

# $eof
