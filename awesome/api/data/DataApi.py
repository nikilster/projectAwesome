from . import DB
from sqlalchemy import func
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

    MAX_VISIONS = 20

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
    def setProfilePicture(userModel, url):
        '''Returns True if a change was made, and False otherwise.'''
        assert userModel, "Invalid user model"
        if userModel.picture != url:
            userModel.picture = url
            DB.session.add(userModel)
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
    # Follow methods
    #

    @staticmethod
    def addFollow(followerModel, userModel):
        '''Add and return new FollowModel to DB (unless it already exists).'''
        existing = DataApi.getFollow(followerModel, userModel)
        if existing != DataApi.NO_OBJECT_EXISTS:
            return existing
        newFollow = FollowModel(followerModel.id, userModel.id, False)
        DB.session.add(newFollow)
        DB.session.commit()
        return newFollow

    @staticmethod
    def removeFollow(followerModel, userModel):
        '''Remove follow from DB. Returns True of successful, else False.'''
        follow = DataApi.getFollow(followerModel, userModel)
        if follow != DataApi.NO_OBJECT_EXISTS:
            DB.session.delete(follow)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def getFollow(followerModel, userModel):
        '''Get follow model, else, NO_OBJECT_EXISTS'''
        follow = FollowModel.query\
                            .filter_by(followerId=followerModel.id)\
                            .filter_by(userId=userModel.id)\
                            .first()
        return follow if None != follow else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def getUserFollowCount(userModel):
        '''Get number of people this user follows'''
        return FollowModel.query\
                          .filter_by(followerId=userModel.id)\
                          .count()

    @staticmethod
    def getUserFollows(userModel, number=0):
        '''Get list of models for people this user follows'''
        query = FollowModel.query\
                           .filter_by(followerId=userModel.id)\
                           .order_by(FollowModel.id.desc())
        if number <= 0:
            return query.all()
        else:
            return query.limit(number)

    @staticmethod
    def getUserFollowerCount(userModel):
        '''Get number of people this user follows'''
        return FollowModel.query\
                          .filter_by(userId=userModel.id)\
                          .count()

    @staticmethod
    def getUserFollowers(userModel, number=0):
        '''Get list of models for people following this user'''
        query = FollowModel.query\
                           .filter_by(userId=userModel.id)\
                           .order_by(FollowModel.id.desc())
        if number <= 0:
            return query.all()
        else:
            return query.limit(number)

    @staticmethod
    def getUserFollowsFromList(userModel, userIds):
        '''Get list of where userModel follows people in list of userIds'''
        if len(userIds) > 0:
            return FollowModel.query\
                              .filter_by(followerId=userModel.id)\
                              .filter(FollowModel.userId.in_(userIds))\
                              .all()
        return []


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
    def visionHasCommentsFromOthers(visionModel, userId):
        '''Returns True if vision has some comments, False otherwise.'''
        assert visionModel != DataApi.NO_OBJECT_EXISTS, "Invalid vision modal"
        comment = VisionCommentModel.query.filter_by(visionId=visionModel.id) \
                                          .filter_by(removed=False) \
                                          .filter(VisionCommentModel.authorId != userId)\
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

        Returns the new vision id, or NO_OBJECT_EXISTS_ID
        '''
        assert userModel, "Invalid user model"

        # get vision list
        userId = userModel.id
        visionListModel = DataApi.getVisionListModelForUser(userModel)
        assert DataApi.NO_OBJECT_EXISTS != visionListModel, "No vision list"

        # ensure we can add a vision
        visionIds = visionListModel.getVisionIdList()
        if len(visionIds) >= DataApi.MAX_VISIONS:
            return DataApi.NO_OBJECT_EXISTS_ID

        vision = VisionModel(userId, text, pictureId, parentId, rootId, privacy)
        DB.session.add(vision)
        DB.session.flush() # flush so vision.id is valid

        # if rootId == 0, root should be self
        if rootId == 0:
            vision.rootId = vision.id
            DB.session.add(vision)

        # now add to vision list
        visionIds.insert(0, vision.id)
        visionListModel.setVisionIdList(visionIds)
        DB.session.add(visionListModel)

        DB.session.commit()

        assert vision.rootId != 0, "Root ID should never be zero"

        return vision.id

    @staticmethod
    def repostVision(userModel, visionModel, isPublic):
        '''Reposts a vision to user's vision list.

        Returns new vision id if successful, NO_OBJECT_EXISTS_ID otherwise.
        '''
        assert userModel, "Invalid user model"
        assert visionModel, "Invalid vision model"

        privacy = VisionPrivacy.PRIVATE
        if isPublic:
            privacy = VisionPrivacy.PUBLIC
        return DataApi.addVision(userModel,
                                 visionModel.text,
                                 visionModel.pictureId,
                                 visionModel.id,
                                 visionModel.rootId,
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
    def getVisionsById(visionIds, allowRemovedVisions=False):
        '''Get vision models from a list of vision ids.
       
        'allowRemovedVisions': be careful when using. Usually we don't want
                        removed visions. An example of using it now is when
                        we want a list of all parent visions to know who we
                        reposted from.
        '''
        visionModels = []
        if len(visionIds) > 0:
            if allowRemovedVisions:
                all_visions = VisionModel.query \
                                        .filter(VisionModel.id.in_(visionIds)) \
                                        .all()
            else:
                all_visions = VisionModel.query \
                                        .filter_by(removed=False) \
                                        .filter(VisionModel.id.in_(visionIds)) \
                                        .all()
            # hash from visionId to vision
            idToVision = dict([(vision.id, vision) for vision in all_visions])

            for visionId in visionIds:
                visionModels.append(idToVision[visionId])
        return visionModels

    @staticmethod
    def getVisionReposts(vision):
        '''Get last 5 public vision reposts'''
        visions = VisionModel.query \
                             .filter_by(rootId=vision.rootId) \
                             .filter_by(removed=False) \
                             .filter_by(privacy=VisionPrivacy.PUBLIC) \
                             .filter(VisionModel.id != vision.id) \
                             .order_by(VisionModel.id.desc()) \
                             .limit(5)
        visionModels = [model for model in visions]
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
    # Vision Like methods
    #

    @staticmethod
    def getVisionLike(visionModel, userModel):
        like = VisionLikeModel.query.filter_by(visionId=visionModel.id)\
                                    .filter_by(userId=userModel.id)\
                                    .first()
        return like if None != like else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def getVisionLikeCount(visionModel):
        return VisionLikeModel.query.filter_by(visionId=visionModel.id).count()

    @staticmethod
    def getVisionListLikeCount(visionIds):
        if len(visionIds) > 0:
            return DB.session.query(VisionLikeModel.visionId,
                                    func.count(VisionLikeModel.visionId))\
                            .filter(VisionLikeModel.visionId.in_(visionIds))\
                            .group_by(VisionLikeModel.visionId)\
                            .all()
        return []

    @staticmethod
    def getVisionIdsLikedByUser(visionIds, userId):
        if len(visionIds) > 0:
            likes = VisionLikeModel.query\
                             .filter_by(userId=userId)\
                             .filter(VisionLikeModel.visionId.in_(visionIds))\
                             .all()
            return [like.visionId for like in likes]
        return []

    @staticmethod
    def addVisionLike(visionModel, userModel):
        '''Returns new VisionLikeModel, or None'''
        existing = DataApi.getVisionLike(visionModel, userModel)
        if existing != DataApi.NO_OBJECT_EXISTS:
            # if a like is already there, return None
            return None
        like = VisionLikeModel(visionModel.id, userModel.id)
        DB.session.add(like)
        DB.session.commit()
        return like

    @staticmethod
    def removeVisionLike(visionModel, userModel):
        '''Returns True if removed, False if like doesn't exist'''
        like = DataApi.getVisionLike(visionModel, userModel)
        if like != DataApi.NO_OBJECT_EXISTS:
            DB.session.delete(like)
            DB.session.commit()
            return True
        return False


    # 
    # Vision Comment Like methods
    #

    @staticmethod
    def getVisionCommentLike(commentModel, userModel):
        like = VisionCommentLikeModel.query\
                                    .filter_by(visionCommentId=commentModel.id)\
                                    .filter_by(userId=userModel.id)\
                                    .first()
        return like if None != like else DataApi.NO_OBJECT_EXISTS

    @staticmethod
    def getVisionCommentLikeCount(commentModel):
        return VisionCommentLikeModel.query\
                                   .filter_by(visionCommentId=commentModel.id)\
                                   .count()

    @staticmethod
    def addVisionCommentLike(commentModel, userModel):
        '''Returns new VisionCommentLikeModel, or None'''
        existing = DataApi.getVisionCommentLike(commentModel, userModel)
        if existing != DataApi.NO_OBJECT_EXISTS:
            # if a like is already there, return None
            return None
        like = VisionCommentLikeModel(commentModel.id, userModel.id)
        DB.session.add(like)
        DB.session.commit()
        return like

    @staticmethod
    def removeVisionCommentLike(commentModel, userModel):
        '''Returns True if removed, False if like doesn't exist'''
        like = DataApi.getVisionCommentLike(commentModel, userModel)
        if like != DataApi.NO_OBJECT_EXISTS:
            DB.session.delete(like)
            DB.session.commit()
            return True
        return False

    @staticmethod
    def getVisionCommentListLikeCount(commentIds):
        if len(commentIds) > 0:
            return DB.session.query(VisionCommentLikeModel.visionCommentId,
                         func.count(VisionCommentLikeModel.visionCommentId))\
                .filter(VisionCommentLikeModel.visionCommentId.in_(commentIds))\
                .group_by(VisionCommentLikeModel.visionCommentId)\
                .all()
        return []

    @staticmethod
    def getVisionCommentIdsLikedByUser(commentIds, userId):
        if len(commentIds) > 0:
            likes = VisionCommentLikeModel.query\
              .filter_by(userId=userId)\
              .filter(VisionCommentLikeModel.visionCommentId.in_(commentIds))\
              .all()
            return [like.visionCommentId for like in likes]
        return []


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
    def getVisionComment(visionCommentId):
        '''Get vision comment from id, or NO_OBJECT_EXISTS.'''
        comment = VisionCommentModel.query.filter_by(id=visionCommentId).first()
        return comment if None != comment else DataApi.NO_OBJECT_EXISTS

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

# $eof
