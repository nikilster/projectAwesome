from . import DB

from sqlalchemy.sql import desc

from DbSchema import *

from awesome.util.Logger import Logger

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

    # 
    # Vision List methods
    #

    @staticmethod
    def getVisionList(userId):
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
    def addVision(userId, text, pictureId, parentId, rootId):
        # get vision list
        visionListModel = DataApi.getVisionList(userId)
        assert DataApi.NO_OBJECT_EXISTS != visionListModel, "No vision list"

        vision = VisionModel(userId, text, pictureId, parentId, rootId)
        DB.session.add(vision)
        DB.session.flush() # flush so vision.id is valid

        # now add to vision list
        visionList = visionListModel.getVisionList()
        visionList.insert(0, vision.id)
        visionListModel.setVisionList(visionList)
        DB.session.add(visionListModel)

        DB.session.commit()
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
                                 vision.rootId)
    
    @staticmethod
    def getMainPageVisions():
        return VisionModel.query.filter_by(parentId=0) \
                                .filter_by(privacy=VisionPrivacy.SHAREABLE) \
                                .filter_by(removed=False) \
                                .order_by(VisionModel.id.desc()) \
                                .limit(100)

    @staticmethod
    def getVisionsForUser(userId):
        visionListModel = DataApi.getVisionList(userId)
        assert DataApi.NO_OBJECT_EXISTS != visionListModel, "No vision list"

        visionIds = visionListModel.getVisionList()

        visions = []
        if len(visionIds) > 0:
            all_visions = VisionModel.query \
                                     .filter_by(userId=userId) \
                                     .filter_by(removed=False) \
                                     .filter(VisionModel.id.in_(visionIds)) \
                                     .all()
            idToVision = {}
            for vision in all_visions:
                idToVision[vision.id] = vision
            for visionId in visionIds:
                assert visionId in idToVision, "Can't find vision Id"
                visions.append(idToVision[visionId])
            
        return visions

    @staticmethod
    def moveUserVision(userId, visionId, srcIndex, destIndex):
        visionListModel = DataApi.getVisionList(userId)
        if DataApi.NO_OBJECT_EXISTS == visionListModel:
            return False
        
        visionIds = visionListModel.getVisionList()
        length = len(visionIds)

        if srcIndex < 0 or srcIndex >= length or \
           destIndex < 0 or destIndex >= length or \
           visionId != visionIds[srcIndex]:
            return False

        moveId = visionIds.pop(srcIndex)
        visionIds.insert(destIndex, moveId)

        visionListModel.setVisionList(visionIds)
        DB.session.add(visionListModel)
        DB.session.commit()
        return True

    @staticmethod
    def deleteUserVision(userId, visionId):
        vision = DataApi.getVision(visionId)
        if vision.id != userId:
            return False
        vision.removed = True
        DB.session.add(vision)
        DB.commit()
        return True


    # 
    # Picture methods
    #

    @staticmethod
    def getPicture(pictureId):
        picture = PictureModel.query.filter_by(id=pictureId).first()
        return picture if None != picture else DataApi.NO_OBJECT_EXISTS

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
