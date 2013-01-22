from data.DataApi import DataApi

from User import User
from Vision import Vision
from VisionList import VisionList
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

    class FeedItem:
        JOIN = "join"
        FOLLOW = "follow"
        VISION = "vision"

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
        TYPE = 'type'
        USER = 'user'
        FOLLOWING = 'following'
        VISION = 'vision'
        NEW_VISION = 'newVision'
        LIKERS = 'likers'
        COMMENTS = 'comments'
        COMMENT_LIKERS = 'commentLikers'
        RECENT_ACTION = 'recentAction'

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
        unfilteredVisionsModels = DataApi.getVisionsById(visionIds,
                                              allowRemovedVisions=True)

        userIds = set([a.objectId for a in activities 
                            if a.action == Activity.Action.JOIN_SITE])
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

        # At this point we have all the visions models for the activities
        # We need to remove the visions that we shouldn't allow this user to
        # see
        filteredVisionModels = []
        for vision in unfilteredVisionsModels:
            # vision should not be removed, and be either public, or a 
            # private vision you own
            if vision.removed == False and \
               (vision.privacy == VisionPrivacy.PUBLIC or\
                vision.userId == user.id()):
                filteredVisionModels.append(vision)
        visionList = VisionList(filteredVisionModels)

        # Now we have a list of all 
        visionObjs = visionList.toDictionary(options=[Vision.Options.PICTURE,
                                                Vision.Options.USER,
                                                Vision.Options.PARENT_USER,
                                                Vision.Options.COMMENTS,
                                                Vision.Options.LIKES,
                                                Vision.Options.COMMENT_LIKES],
                                             user=user)
        idToVisionObj = dict([(v[Vision.Key.ID], v) for v in visionObjs])

        # Now build activities!
        feedObjList = []
        visionIdToFeedObj = dict()
        for activity in activities:
            # JOIN SITE
            if activity.action == Activity.Action.JOIN_SITE:
                # Already have enough info to render this activity
                newUser  = User(idToUser[activity.subjectId])

                obj = dict()
                obj[Activity.Key.TYPE] = Activity.FeedItem.JOIN
                obj[Activity.Key.USER] = newUser.toDictionary()

                feedObjList.append(obj)
            # FOLLOW
            elif activity.action == Activity.Action.FOLLOW:
                follow = idToFollow[activity.objectId]
                follower = User(idToUser[follow.followerId])
                following = User(idToUser[follow.userId])

                obj = dict()
                obj[Activity.Key.TYPE] = Activity.FeedItem.FOLLOW
                obj[Activity.Key.USER] = follower.toDictionary()
                obj[Activity.Key.FOLLOWING] = following.toDictionary()

                feedObjList.append(obj)
            # VISION-RELATED
            elif activity.action == Activity.Action.ADD_VISION or \
                 activity.action == Activity.Action.LIKE_VISION or \
                 activity.action == Activity.Action.COMMENT_ON_VISION or \
                 activity.action == Activity.Action.LIKE_VISION_COMMENT:

                # get vision we are working with
                visionId = None
                if activity.action == Activity.Action.ADD_VISION:
                    visionId = activity.objectId
                elif activity.action == Activity.Action.LIKE_VISION:
                    visionId = idToVisionLike[activity.objectId].visionId
                elif activity.action == Activity.Action.COMMENT_ON_VISION:
                    visionId = idToComment[activity.objectId].visionId
                elif activity.action == Activity.Action.LIKE_VISION_COMMENT:
                    commentLike = idToCommentLike[activity.objectId]
                    visionId = idToComment[commentLike.visionCommentId]

                # if we don't know vision id from here, ignore this activity
                if visionId == None:
                    continue

                # Get the vision object we will be working with
                if visionId in visionIdToFeedObj:
                    obj = visionIdToFeedObj[visionId]
                else:
                    if visionId in idToVisionObj:
                        obj = dict()
                        actionString = Activity.ACTION_STRING[activity.action]
                        obj[Activity.Key.TYPE] = Activity.FeedItem.VISION
                        obj[Activity.Key.VISION] = idToVisionObj[visionId]
                        obj[Activity.Key.RECENT_ACTION] = actionString

                        feedObjList.append(obj)
                        visionIdToFeedObj[visionId] = obj
                    else:
                        continue

                # now append whatever we can to feed obj based on activity type
                # Vision-related objects fill in these keys:
                #   VISION - the vision we are working with (with USER in it)
                #            (this should already be filled in)
                #   NEW_VISION - T/F if ADD_VISION activity is seen
                #   LIKER - list of Users that liked vision
                #   COMMENTS - list of comments with AUTHOR
                #   COMMENT_LIKES - list of comment likes info:
                #       USER - user that liked the comment
                #       COMMENT - comment info
                if activity.action == Activity.Action.ADD_VISION:
                    obj[Activity.Key.NEW_VISION] = True
                elif activity.action == Activity.Action.LIKE_VISION:
                    # get liker
                    liker = User(idToUser[activity.subjectId])

                    if Activity.Key.LIKERS in obj:
                        # If a likers list exists, find out if user is already
                        # in the list. Only add if the user isn't
                        existing = [l['id'] for l in obj[Activity.Key.LIKERS]]
                        if liker.id() not in existing:
                            likerObj = liker.toDictionary()
                            obj[Activity.Key.LIKERS].append(likerObj)
                    else:
                        # Else, create the list and enter the liker into it
                        obj[Activity.Key.LIKERS] = [liker.toDictionary()]
                elif activity.action == Activity.Action.COMMENT_ON_VISION:
                    # get comment
                    comment = VisionComment(idToComment[activity.objectId])

                    if Activity.Key.COMMENTS in obj:
                        existing = [c['id'] for c in obj[Activity.Key.COMMENTS]]
                        if comment.id() not in existing:
                            commentObj = comment.toDictionary()
                            author = User(idToUser[comment.authorId()])
                            authorObj = author.toDictionary()
                            commentObj[VisionComment.Key.AUTHOR] = authorObj
                            obj[Activity.Key.COMMENTS].append(commentObj)
                    else:
                        commentObj = comment.toDictionary()
                        author = User(idToUser[comment.authorId()])
                        authorObj = author.toDictionary()
                        commentObj[VisionComment.Key.AUTHOR] = authorObj
                        obj[Activity.Key.COMMENTS] = [commentObj]
                elif activity.action == Activity.Action.LIKE_VISION_COMMENT:
                    # get liker
                    commentLike = idToCommentLike[activity.subjectId]
                    liker = User(idToUser[commentLike.userId])

                    if Activity.Key.COMMENT_LIKERS in obj:
                        # If a likers list exists, find out if user is already
                        # in the list. Only add if the user isn't
                        existing = [l['id'] 
                                     for l in obj[Activity.Key.COMMENT_LIKERS]]
                        if liker.id() not in existing:
                            obj[Activity.Key.COMMENT_LIKERS].append(likerObj)
                    else:
                        # Else, create the list and enter the liker into it
                        likerObj = liker.toDictionary()
                        obj[Activity.Key.COMMENT_LIKERS] = [likerObj]
                else:
                    pass
        return feedObjList


        '''
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
        '''
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
