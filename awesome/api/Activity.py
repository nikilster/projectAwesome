from data.DataApi import DataApi

from User import User
from Vision import Vision
from VisionComment import VisionComment
from Picture import Picture
from Privacy import VisionPrivacy

from ..util.Logger import Logger

class Activity:
    '''Generic activity class'''

    class Action:
        '''Enum for types for Activities actions'''
        # User actions
        JOIN_SITE = 0
        UPDATE_PROFILE_PICTURE = 1
        UPDATE_DESCRIPTION = 2

        # Vision and vision comment actions
        ADD_VISION = 20
        LIKE_VISION = 21
        COMMENT_ON_VISION = 22
        LIKE_VISION_COMMENT = 23

        # Social actions
        FOLLOW = 40

    ACTION_STRING = {
        Action.JOIN_SITE : "joinSite",
        Action.UPDATE_PROFILE_PICTURE : "updateProfilePicture",
        Action.UPDATE_DESCRIPTION : "updateDescription",

        # Vision and vision comment actions
        Action.ADD_VISION : "addVision",
        Action.LIKE_VISION : "likeVision",
        Action.COMMENT_ON_VISION : "commentOnVision",
        Action.LIKE_VISION_COMMENT : "likeVisionComment",

        # Social actions
        Action.FOLLOW : "follow",
    }

    class Key:
        Action = 'action'
        User = 'user'
        Following = 'following'
        Vision = 'vision'
        VisionComment = 'visionComment'

    #
    # Static methods
    #

    @staticmethod
    def getUserFeed(user):
        # Get set of all userIds to fetch activities from
        # This includes following ids, and own userId
        follows = user.getFollows()
        userIds = set()
        for f in follows.followList():
            userIds.add(f.userId())
        userIds.add(user.id())
  
        # Fetch activities
        activities = DataApi.getActivities(userIds)

        # Fetch all objects and create dictonary objects now. Might as well
        # here for now since we don't need anything else yet.
        # TODO: probably will need to change later

        followIds = set([a.objectId for a in activities 
                            if a.action == Activity.Action.FOLLOW])
        commentLikeIds = set([a.objectId for a in activities 
                            if a.action == Activity.Action.LIKE_VISION_COMMENT])
        visionLikeIds = set([a.objectId for a in activities 
                            if a.action == Activity.Action.LIKE_VISION])
        followModels = DataApi.getFollowsById(followIds)
        commentLikeModels = DataApi.getVisionCommentLikesById(commentLikeIds)
        visionLikeModels = DataApi.getVisionLikesById(visionLikeIds)

        idToFollow = dict([(f.id, f) for f in followModels])
        idToCommentLike = dict([(l.id, l) for l in commentLikeModels])
        idToVisionLike = dict([(l.id, l) for l in visionLikeModels])

        commentIds = set([a.objectId for a in activities 
                            if a.action == Activity.Action.COMMENT_ON_VISION])
        for l in commentLikeModels:
            commentIds.add(l.visionCommentId)
        commentModels = DataApi.getVisionCommentsById(commentIds)
        idToComment = dict([(c.id, c) for c in commentModels])

        visionIds = set([a.objectId for a in activities 
                            if a.action == Activity.Action.ADD_VISION])
        for c in commentModels:
            visionIds.add(c.visionId)
        for l in visionLikeModels:
            visionIds.add(l.visionId)
        visionModels = DataApi.getVisionsById(visionIds,
                                              allowRemovedVisions=True)
        idToVision = dict([(v.id, v) for v in visionModels])

        pictureIds = set([v.pictureId for v in visionModels])
        pictureModels = DataApi.getPicturesFromIds(pictureIds)
        idToPicture = dict([(p.id, p) for p in pictureModels])

        userIds = set([a.objectId for a in activities 
                            if a.action == Activity.Action.JOIN_SITE])
        for v in visionModels:
            userIds.add(v.userId)
        for c in commentModels:
            userIds.add(c.authorId)
        for l in visionLikeModels:
            userIds.add(l.userId)
        for l in commentLikeModels:
            userIds.add(l.userId)
        for f in followModels:
            userIds.add(f.followerId)
            userIds.add(f.userId)
        userModels = DataApi.getUsersFromIds(userIds)
        idToUser = dict([(u.id, u) for u in userModels])

        def getVisionDict(id):
            if not (id in idToVision):
                return None
            model = idToVision[id]
            vision = Vision(model)
            if vision.removed() == True or \
               (vision.privacy() == VisionPrivacy.PRIVATE and\
                vision.userId() != user.id()):
                return None
            obj = vision.toDictionary()
            obj[Vision.Key.PICTURE] = Picture(idToPicture[vision.pictureId()]).toDictionary()
            obj[Vision.Key.USER] = User(idToUser[vision.userId()]).toDictionary()
            return obj

        objList = []
        for activity in activities:
            obj = dict()
            obj[Activity.Key.Action] = Activity.ACTION_STRING[activity.action]
            obj[Activity.Key.User] = User(idToUser[activity.subjectId]).toDictionary()

            # JOIN SITE
            if activity.action == Activity.Action.JOIN_SITE:
                # Already have enough info to render this activity
                pass
            # ADD VISION or LIKE VISION
            elif activity.action == Activity.Action.ADD_VISION or \
                 activity.action == Activity.Action.LIKE_VISION:
                if activity.action == Activity.Action.ADD_VISION:
                    vision = getVisionDict(activity.objectId)
                else:
                    vision = getVisionDict(idToVisionLike[activity.objectId].visionId)
                    
                if vision:
                    obj[Activity.Key.Vision] = vision
                else:
                    obj = None
            # COMMENT ON VISION or LIKE VISION COMMENT
            elif activity.action == Activity.Action.COMMENT_ON_VISION or \
                 activity.action == Activity.Action.LIKE_VISION_COMMENT:
                if activity.action == Activity.Action.COMMENT_ON_VISION:
                    comment = VisionComment(idToComment[activity.objectId])
                else:
                    comment = VisionComment(idToComment[idToCommentLike[activity.objectId].visionCommentId])
                vision = getVisionDict(comment.visionId())
                if vision:
                    commentObj = comment.toDictionary()
                    commentObj[VisionComment.Key.AUTHOR] = User(idToUser[comment.authorId()]).toDictionary()
                    obj[Activity.Key.VisionComment] = commentObj
                    obj[Activity.Key.Vision] = vision
                else:
                    obj = None
            # FOLLOW
            elif activity.action == Activity.Action.FOLLOW:
                obj[Activity.Key.Following] = User(idToUser[idToFollow[activity.objectId].userId]).toDictionary()
            else:
                obj = None
            if obj:
                objList.append(obj)
        return objList

    #
    # Private methods
    #
    def __init__(self, model):
        assert model, "Invalid activity model"
        self._model = model
  
    # internal getters
    def _subjectId(self):
        return self._model.subjectId
    def _action(self):
        return self._model.action
    def _objectId(self):
        return self._model.objectId

# $eof
