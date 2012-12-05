from . import DB

from sqlalchemy.ext.hybrid import hybrid_property

import datetime
import json

S3_HTTPS_HEADER = 'https://s3.amazonaws.com/'

class UserPrivacy:
    PRIVATE = 0
    PUBLIC = 1

class VisionPrivacy:
    PRIVATE = 0
    SHAREABLE = 1

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

    created         = DB.Column(DB.DateTime, default=datetime.datetime.utcnow)
    modified        = DB.Column(DB.DateTime, default=datetime.datetime.utcnow,
                                            onupdate=datetime.datetime.utcnow)
    privacy         = DB.Column(DB.Integer, default=UserPrivacy.PRIVATE)

    @hybrid_property
    def fullName(self):
        return self.firstName + " " + self.lastName

    def __init__(self, firstName, lastName, email, passwordHash):
        self.firstName = firstName
        self.lastName = lastName
        self.passwordHash = passwordHash
        self.email = email
        self.userName = ""

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

    # for future use
    privacy         = DB.Column(DB.Integer, default=VisionPrivacy.SHAREABLE)

    def __init__(self, userId, text, pictureId, parentId, rootId):
        self.userId = userId
        self.text = text
        self.pictureId = pictureId
        self.parentId = parentId
        self.rootId = rootId
    def __str__(self):
        return '<Vision %s>' % str(self.id)

    def toDictionary(self):
        '''
        picture = {}
        if self.pictureId > 0:
            # TODO: This is slow but lets worry about it later
            model = PictureModel.query.filter_by(id=self.pictureId).first()
            if model != None:
                picture = model.toDictionary()
        '''
        return {'id' : self.id,
                'userId' : self.userId,
                'text' : self.text,
                'parentId' : self.parentId,
                'rootId' : self.rootId,
                #'picture' : picture,
               }

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

    def toDictionary(self):
        return { 'id' : self.id,
                 'largeUrl' : self.largeUrl,
                 'mediumUrl' : self.mediumUrl,
                 'smallUrl' : self.smallUrl,
               }
# $eof
