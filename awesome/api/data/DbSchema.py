from . import DB

from sqlalchemy.ext.hybrid import hybrid_property

import datetime
import json

from ..Privacy import UserPrivacy, VisionPrivacy

S3_HTTPS_HEADER = 'https://s3.amazonaws.com/'

#
# UserModel
#
class UserModel(DB.Model):
    __tablename__   = 'user'
    id              = DB.Column(DB.BigInteger(unsigned=True), primary_key=True)
    firstName       = DB.Column(DB.String(40))
    lastName        = DB.Column(DB.String(40))
    passwordHash    = DB.Column(DB.String(60))

    email           = DB.Column(DB.String(255), unique=True)
    emailConfirmed  = DB.Column(DB.Boolean, default=False)

    picture         = DB.Column(DB.Text)

    description     = DB.Column(DB.Text)
    visionPrivacy   = DB.Column(DB.Integer, default=VisionPrivacy.PUBLIC)

    created         = DB.Column(DB.DateTime, default=datetime.datetime.utcnow)
    modified        = DB.Column(DB.DateTime, default=datetime.datetime.utcnow,
                                            onupdate=datetime.datetime.utcnow)
    privacy         = DB.Column(DB.Integer, default=UserPrivacy.PUBLIC)

    utcOffset       = DB.Column(DB.Integer, default=0)

    dailyEmail      = DB.Column(DB.Boolean, default=True)

    @hybrid_property
    def fullName(self):
        return self.firstName + " " + self.lastName

    def __init__(self, firstName, lastName, email, passwordHash):
        self.firstName = firstName
        self.lastName = lastName
        self.passwordHash = passwordHash
        self.email = email
        self.userName = ""
        self.picture = "https://s3.amazonaws.com/project-awesome-img/img/default-profile-picture.jpg"
        self.description = ""

    def __str__(self):
        return '<User %s:%s %s>' % (self.id, self.firstName, self.lastName)

#
# VisionListModel : JSON list of vision ids
#
class VisionListModel(DB.Model):
    __tablename__   = 'vision_list'
    id              = DB.Column(DB.BigInteger(unsigned=True), primary_key=True)
    userId          = DB.Column(DB.BigInteger(unsigned=True), index=True)
    visionJson      = DB.Column(DB.Text)

    created         = DB.Column(DB.DateTime, default=datetime.datetime.utcnow)
    modified        = DB.Column(DB.DateTime, default=datetime.datetime.utcnow,
                                             onupdate=datetime.datetime.utcnow)

    def __init__(self, userId):
        self.userId = userId
        self.visionJson = "[]"
    
    def __str__(self):
        return '<VisionList %s>' % str(self.id)

    # Use these to set and get from the JSON list
    def getVisionIdList(self):
        return json.loads(self.visionJson)
    
    def setVisionIdList(self, visionList):
        self.visionJson = json.dumps(visionList)


#
# VisionModel
#
class VisionModel(DB.Model):
    __tablename__   = 'vision'
    id              = DB.Column(DB.BigInteger(unsigned=True), primary_key=True)
    userId          = DB.Column(DB.BigInteger(unsigned=True), index=True)
    text            = DB.Column(DB.Text)
    pictureId       = DB.Column(DB.BigInteger(unsigned=True), index=True)

    parentId        = DB.Column(DB.BigInteger(unsigned=True), index=True)
    rootId          = DB.Column(DB.BigInteger(unsigned=True), index=True)

    removed         = DB.Column(DB.Boolean, default=False)

    created         = DB.Column(DB.DateTime, default=datetime.datetime.utcnow)
    modified        = DB.Column(DB.DateTime, default=datetime.datetime.utcnow,
                                             onupdate=datetime.datetime.utcnow)

    privacy         = DB.Column(DB.Integer, default=VisionPrivacy.PRIVATE)

    def __init__(self, userId, text, pictureId,
                 parentId, rootId,
                 privacy):
        assert privacy >= 0 and privacy < VisionPrivacy.INVALID, "Invalid vision privacy value"
        self.userId = userId
        self.text = text
        self.pictureId = pictureId
        self.parentId = parentId
        self.rootId = rootId
        self.privacy = privacy
    def __str__(self):
        return '<Vision %s>' % str(self.id)


#
# PictureModel
#
# Only have user_id for if we ever need to know who uploaded a picture. We
# may need this if Privacy & Terms of Service says that the user owns their
# content.
#
class PictureModel(DB.Model):
    __tablename__   = 'picture'
    id              = DB.Column(DB.BigInteger(unsigned=True), primary_key=True)
    userId          = DB.Column(DB.BigInteger(unsigned=True))

    original        = DB.Column(DB.Text) # Either URL or original file name
    uploaded        = DB.Column(DB.Boolean) # T for uploaded file, F for URL

    s3Bucket        = DB.Column(DB.Text)

    origKey         = DB.Column(DB.Text)
    origWidth       = DB.Column(DB.Integer(unsigned=True))
    origHeight      = DB.Column(DB.Integer(unsigned=True))

    largeKey        = DB.Column(DB.Text)
    largeWidth      = DB.Column(DB.Integer(unsigned=True))
    largeHeight     = DB.Column(DB.Integer(unsigned=True))

    mediumKey       = DB.Column(DB.Text)
    mediumWidth     = DB.Column(DB.Integer(unsigned=True))
    mediumHeight    = DB.Column(DB.Integer(unsigned=True))

    smallKey        = DB.Column(DB.Text)
    smallWidth      = DB.Column(DB.Integer(unsigned=True))
    smallHeight     = DB.Column(DB.Integer(unsigned=True))

    created         = DB.Column(DB.DateTime, default=datetime.datetime.utcnow)
    modified        = DB.Column(DB.DateTime, default=datetime.datetime.utcnow,
                                             onupdate=datetime.datetime.utcnow)
    removed         = DB.Column(DB.Boolean, default=False)

    @hybrid_property
    def largeUrl(self):
        return S3_HTTPS_HEADER + self.s3Bucket + "/" + self.largeKey

    @hybrid_property
    def mediumUrl(self):
        return S3_HTTPS_HEADER + self.s3Bucket + "/" + self.mediumKey

    @hybrid_property
    def smallUrl(self):
        return S3_HTTPS_HEADER + self.s3Bucket + "/" + self.smallKey

    def __init__(self, userId, original, uploaded, s3Bucket,
                       origKey, origWidth, origHeight,
                       largeKey, largeWidth, largeHeight,
                       mediumKey, mediumWidth, mediumHeight,
                       smallKey, smallWidth, smallHeight):
        self.userId = userId
        self.original = original
        self.uploaded = uploaded
        self.s3Bucket = s3Bucket
        self.origKey = origKey
        self.origWidth = origWidth
        self.origHeight = origHeight
        self.largeKey = largeKey
        self.largeWidth = largeWidth
        self.largeHeight = largeHeight
        self.mediumKey = mediumKey
        self.mediumWidth = mediumWidth
        self.mediumHeight = mediumHeight
        self.smallKey = smallKey
        self.smallWidth = smallWidth
        self.smallHeight = smallHeight

    def __str__(self):
        return '<Picture %s>' % str(self.id)

#
# VisionComment
#
class VisionCommentModel(DB.Model):
    __tablename__   = 'vision_comment'
    id              = DB.Column(DB.BigInteger(unsigned=True), primary_key=True)
    visionId        = DB.Column(DB.BigInteger(unsigned=True), index=True)
    authorId        = DB.Column(DB.BigInteger(unsigned=True), index=True)

    pictureId       = DB.Column(DB.BigInteger(unsigned=True), default=0)

    text            = DB.Column(DB.Text)

    created         = DB.Column(DB.DateTime, default=datetime.datetime.utcnow)
    modified        = DB.Column(DB.DateTime, default=datetime.datetime.utcnow,
                                             onupdate=datetime.datetime.utcnow)
    removed         = DB.Column(DB.Boolean, default=False)

    def __init__(self, visionId, authorId, text):
        self.visionId = visionId
        self.authorId = authorId
        self.text = text
    def __str__(self):
        return '<VisionComment %s>' % (str(self.id))

#
# VisionLike
#
class VisionLikeModel(DB.Model):
    __tablename__   = 'vision_like'
    id              = DB.Column(DB.BigInteger(unsigned=True), primary_key=True)
    visionId        = DB.Column(DB.BigInteger(unsigned=True), index=True)
    userId          = DB.Column(DB.BigInteger(unsigned=True), index=True)
    created         = DB.Column(DB.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, visionId, userId):
        self.visionId = visionId
        self.userId = userId
    def __str__(self):
        return '<VisionLike %s:%s>' % (str(self.visionId), str(self.userId))

#
# VisionCommentLike
#
class VisionCommentLikeModel(DB.Model):
    __tablename__   = 'vision_comment_like'
    id              = DB.Column(DB.BigInteger(unsigned=True), primary_key=True)
    visionCommentId = DB.Column(DB.BigInteger(unsigned=True), index=True)
    userId          = DB.Column(DB.BigInteger(unsigned=True), index=True)
    created         = DB.Column(DB.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, visionCommentId, userId):
        self.visionCommentId = visionCommentId
        self.userId = userId
    def __str__(self):
        return '<VisionCommentLike %s:%s>' % (str(self.visionCommentId),
                                              str(self.userId))

#
# FollowModel: Represents a follow from follower -> user
#
# Meaning follower is following the shared data of user
#
class FollowModel(DB.Model):
    __tablename__   = 'follow'
    id              = DB.Column(DB.BigInteger(unsigned=True), primary_key=True)
    followerId      = DB.Column(DB.BigInteger(unsigned=True), index=True)
    userId          = DB.Column(DB.BigInteger(unsigned=True), index=True)
    blessed         = DB.Column(DB.Boolean, default=False)

    created         = DB.Column(DB.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, followerId, userId, blessed):
        self.followerId = followerId
        self.userId = userId
        self.blessed = blessed
    def __str__(self):
        return '<Follow %s:%s:%s>' % (str(self.followerId),
                                      str(self.userId),
                                      str(self.blessed))


#
# ActivityModel: Represents an activity in the news feed
#
# Every activity is: <subject> <action> <object>
#
class ActivityModel(DB.Model):
    __tablename__   = 'activity'
    id              = DB.Column(DB.BigInteger(unsigned=True), primary_key=True)
    subjectId       = DB.Column(DB.BigInteger(unsigned=True), index=True)
    action          = DB.Column(DB.Integer, index=True)
    objectId        = DB.Column(DB.BigInteger(unsigned=True), index=True)
    extraJson       = DB.Column(DB.Text())

    created         = DB.Column(DB.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, subjectId, action, objectId):
        self.subjectId = subjectId
        self.action = action
        self.objectId = objectId
        self.extraJson = ""
    def __str__(self):
        return '<Activity %s:%s:%s>' % (str(self.subjectId),
                                      str(self.action),
                                      str(self.objectId))

# $eof
