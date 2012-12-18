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
    #

    @staticmethod
    def getUserById(userId):
        '''Get user model by user id, else, NO_OBJECT_EXISTS'''
        user = UserModel.query.filter_by(id=userId).first()
        return user if None != user else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def getUserByEmail(email):
        '''Get user model by email address, else, NO_OBJECT_EXISTS'''
        user = UserModel.query.filter_by(email=email).first()
        return user if None != user else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def setUserName(userModel, firstName, lastName):
        '''Returns True if a change was made, and False otherwise.'''
        assert userModel, "Invalid user model"
        change = False
        if userModel.firstName != firstName:
            userModel.firstName = firstName
            change = True
        if userModel.lastName != lastName:
            userModel.lastName = lastName
            change = True

        if change == True:
            DB.session.add(userModel)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def setUserEmail(userModel, email):
        '''Returns True if a change was made, and False otherwise.'''
        assert userModel, "Invalid user model"
        if email != userModel.email:
            # there shouldn't be another user with this email address
            userByEmail = DataApi.getUserByEmail(email)
            if DataApi.NO_OBJECT_EXISTS != userByEmail:
                userModel.email = email
                DB.session.add(userModel)
                DB.session.commit()
                return True
        return False

    @staticmethod
    def setUserVisionPrivacy(userModel, visionPrivacy):
        '''Returns True if a change was made, and False otherwise.'''
        assert userModel, "Invalid user model"
        if userModel.visionPrivacy != visionPrivacy:
            userModel.visionPrivacy = visionPrivacy
            DB.session.add(userModel)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def setUserDescription(userModel, desc):
        '''Returns True if a change was made, and False otherwise.'''
        assert userModel, "Invalid user model"
        if userModel.description != desc:
            userModel.description = desc
            DB.session.add(userModel)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def setUserPasswordHash(userId, passwordHash):
        '''Returns True if a change was made, and False otherwise.'''
        assert userModel, "Invalid user model"
        if userModel.passwordHash != passwordHash:
            userModel.passwordHash = passwordHash
            DB.session.add(userModel)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def setProfilePicture(userId, url):
        '''Returns True if a change was made, and False otherwise.'''
        assert userModel, "Invalid user model"
        if user.picture != url:
            user.picture = url
            DB.session.add(user)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def addUser(firstName, lastName, email, passwordHash):
        '''Creates a new user and returns the new user id.'''
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
        '''Gets user models from a list of user ids'''
        if len(userIds) > 0:
            return UserModel.query \
                        .filter(UserModel.id.in_(userIds)) \
                        .all()
        return []

    @staticmethod
    def getAllUsers():
        '''Gets all user models'''
        return UserModel.query.all();

    #
    # VisionListModel-related DB methods
    #

    @staticmethod
    def getVisionListModelForUser(userModel):
        '''Returns the VisionListModel for a user id, or NO_OBJECT_EXISTS.'''
        assert userModel, "Invalid user model"
        visionList = VisionListModel.query \
                                    .filter_by(userId=userModel.id). \
                                    first()
        return visionList if None != visionList else DataApi.NO_OBJECT_EXISTS


    @staticmethod
    def getVisionIdListForUser(userModel):
        '''Returns list of vision ids for a user, or NO_OBJECT_EXISTS.'''
        assert userModel, "Invalid user model"
        visionListModel = DataApi.getVisionListModelForUser(userModel)
        if visionListModel != None:
            return visionListModel.getVisionIdList() 
        else:
            return DataApi.NO_OBJECT_EXISTS


    # 
    # Vision methods
    #

    @staticmethod
    def getVision(visionId):
        '''Get vision from vision id, or NO_OBJECT_EXISTS.'''
        vision = VisionModel.query.filter_by(id=visionId).first()
        return vision if None != vision else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def visionHasComments(visionModel):
        '''Returns True if vision has some comments, False otherwise.'''
        assert visionModel != DataApi.NO_OBJECT_EXISTS, "Invalid vision modal"
        comment = VisionCommentModel.query.filter_by(visionId=visionModel.id) \
                                          .filter_by(removed=False) \
                                          .first()
        return True if None != comment else False

    @staticmethod
    def editVision(visionModel, text, privacy):
        '''Returns true if text or privacy changed.'''
        assert visionModel != DataApi.NO_OBJECT_EXISTS, "Invalid vision modal"
        change = False
        if text != visionModel.text:
            visionModel.text = text
            change = True
        if privacy != visionModel.privacy:
            visionModel.privacy = privacy
            change = True
        if change:
            DB.session.add(visionModel)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def addVision(userModel, text, pictureId, parentId, rootId, privacy):
        '''Adds new vision to beginning of a user's vision list.

        Returns the new vision id.
        '''
        assert userModel, "Invalid user model"

        # get vision list
        userId = userModel.id
        visionListModel = DataApi.getVisionListModelForUser(userModel)
        assert DataApi.NO_OBJECT_EXISTS != visionListModel, "No vision list"

        vision = VisionModel(userId, text, pictureId, parentId, rootId, privacy)
        DB.session.add(vision)
        DB.session.flush() # flush so vision.id is valid

        # if rootId == 0, root should be self
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
    def repostVision(userModel, visionId, isPublic):
        '''Reposts a vision to user's vision list.

        Returns new vision id if successful, NO_OBJECT_EXISTS_ID otherwise.
        '''
        assert userModel, "Invalid user model"

        vision = DataApi.getVision(visionId)
        if DataApi.NO_OBJECT_EXISTS == vision:
            return DataApi.NO_OBJECT_EXISTS_ID

        privacy = VisionPrivacy.SHAREABLE
        if isPublic:
            privacy = VisionPrivacy.PUBLIC
        return DataApi.addVision(userModel,
                                 vision.text,
                                 vision.pictureId,
                                 vision.id,
                                 vision.rootId,
                                 privacy)
    
    @staticmethod
    def getMainPageVisions():
        '''Get first 100 original vision models (where parentId == 0)'''
        return VisionModel.query.filter_by(parentId=0) \
                                .filter_by(privacy=VisionPrivacy.PUBLIC) \
                                .filter_by(removed=False) \
                                .order_by(VisionModel.id.desc()) \
                                .limit(100)

    @staticmethod
    def getVisionsForUser(userModel):
        '''Get vision models for a user's vision list.'''
        visionIds = DataApi.getVisionIdListForUser(userModel)
        assert DataApi.NO_OBJECT_EXISTS != visionIds, "Invalid vision list"
        visionModels = []
        if len(visionIds) > 0:
            all_visions = VisionModel.query \
                                     .filter_by(userId=userModel.id) \
                                     .filter_by(removed=False) \
                                     .filter(VisionModel.id.in_(visionIds)) \
                                     .all()

            # hash from visionId to vision
            idToVision = dict([(vision.id, vision) for vision in all_visions])

            visionModels = [idToVision[visionId] for visionId in visionIds]
        return visionModels


    @staticmethod
    def moveUserVision(userModel, visionId, srcIndex, destIndex):
        '''Move a vision in a user's vision list order.
        
        Returns True if move was made, False otherwise.
        '''
        assert userModel, "Invalid user model."
        visionListModel = DataApi.getVisionListModelForUser(userModel)
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
    def deleteUserVision(userModel, visionId):
        '''Returns True of remove is successful, False otherwise.'''
        assert userModel, "Invalid user model"
        visionModel = DataApi.getVision(visionId)
        if visionModel == DataApi.NO_OBJECT_EXISTS:
            return False
        if visionModel.removed == True:
            return False

        visionListModel = DataApi.getVisionListModelForUser(userModel)
        visionIds = visionListModel.getVisionIdList()

        if visionModel.userId != userModel.id:
            return False
        if not (visionModel.id in visionIds):
            return False

        # mark the vision as removed
        visionModel.removed = True
        DB.session.add(visionModel)

        # now remove from vision list
        visionIds.remove(visionModel.id)
        visionListModel.setVisionIdList(visionIds)
        DB.session.add(visionListModel)

        DB.session.commit()
        return True

    # 
    # Vision Comment methods
    #
    @staticmethod
    def addVisionComment(visionModel, authorModel, text):
        '''Returns new VisionCommentModel.'''
        assert visionModel, "Invalid vision model"
        assert authorModel, "Invalid user model"
        comment = VisionCommentModel(visionModel.id, authorModel.id, text)
        DB.session.add(comment)
        DB.session.commit()
        return comment

    @staticmethod
    def getVisionComments(visionModel, maxComments):
        '''Returns up to maxComments number of recent VisionCommentModels'''
        assert maxComments > 0 and maxComments < 1000, \
               "Invalid max comments value"
        comments = VisionCommentModel.query \
                                     .filter_by(removed=False) \
                                     .filter_by(visionId=visionModel.id) \
                                     .order_by(VisionCommentModel.id.desc()) \
                                     .limit(maxComments)

        # reverse order since we retried them in decreasing id order
        return [comment for comment in reversed([c for c in comments])]

    # 
    # Picture methods
    #

    @staticmethod
    def getPicture(pictureId):
        '''Returns PictureModel or NO_OBJECT_EXISTS.'''
        picture = PictureModel.query.filter_by(id=pictureId).first()
        return picture if None != picture else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def getPicturesFromIds(pictureIds):
        '''Returns PictureModels for the given list of picture ids.'''
        if len(pictureIds) > 0:
            return PictureModel.query \
                            .filter_by(removed=False) \
                            .filter(PictureModel.id.in_(pictureIds)) \
                            .all()
        return []

    @staticmethod
    def addPicture(userModel, original, uploaded, s3Bucket,
                           origKey, origWidth, origHeight,
                           largeKey, largeWidth, largeHeight,
                           mediumKey, mediumWidth, mediumHeight,
                           smallKey, smallWidth, smallHeight):
        '''Returns new picture id'''
        assert userModel, "Invalid user model."
        # new PictureModel
        picture = PictureModel(userModel.id, original, uploaded, s3Bucket,
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
    def getRandomVision(userModel):
        '''Gets random vision for a user.'''
        visionIdList = DataApi.getVisionIdListForUser(userModel)
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
        '''Gets all users and a random vision for each.'''
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
