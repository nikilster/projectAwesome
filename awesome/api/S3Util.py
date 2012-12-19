#
# ImageUtil.py
#
# Utility functions for managing images
#

from werkzeug import secure_filename
import os, calendar, datetime, hashlib
from math import floor, ceil

from boto.s3.key import Key
import pycurl
from PIL import Image

from .. import app
from .. import S3_CONN, S3_BUCKET_NAME, S3_HTTPS_HEADER

from ..util.Verifier import Verifier
from ..util.Logger import Logger

GET_URL_CONNECT_TIMEOUT = 5
GET_URL_TIMEOUT = 10
GET_URL_MAX_FILE_SIZE = 5 * 1024 * 1024
GET_URL_MAX_REDIRECTS = 5

VISION_LARGE_WIDTH = 600
VISION_MEDIUM_WIDTH = 275
VISION_SMALL_WIDTH = 150
VISION_THUMBNAIL_WIDTH = 100

PROFILE_PICTURE_WIDTH = 175

# Dictionary defining supported image types and their associated ContentType
IMAGE_TYPES = dict({
    'png'   : 'image/png',
    'jpg'   : 'image/jpeg',
    'jpeg'  : 'image/jpeg',
    'gif'   : 'image/gif',
    'bmp'   : 'image/x-ms-bmp',   # this one is unofficial
})

def fileExt(filename):
    parts = filename.rsplit('.',1)
    if len(parts) < 2:
        return None
    return parts[1].lower()

def contentType(filename):
    ext = fileExt(filename)
    if ext and ext in IMAGE_TYPES.keys():
        return IMAGE_TYPES[ext]
    return None


# Class to help pass around S3-related vision info
class S3Vision:
    def __init__(self, s3Bucket,
                       origKey, origWidth, origHeight,
                       largeKey, largeWidth, largeHeight,
                       mediumKey, mediumWidth, mediumHeight,
                       smallKey, smallWidth, smallHeight):
        self._s3Bucket = s3Bucket

        self._origKey = origKey
        self._origWidth = origWidth
        self._origHeight = origHeight

        self._largeKey = largeKey
        self._largeWidth = largeWidth
        self._largeHeight = largeHeight

        self._mediumKey = mediumKey
        self._mediumWidth = mediumWidth
        self._mediumHeight = mediumHeight

        self._smallKey = smallKey
        self._smallWidth = smallWidth
        self._smallHeight = smallHeight

    def s3Bucket(self):
        return self._s3Bucket
    def origKey(self):
        return self._origKey
    def origWidth(self):
        return self._origWidth
    def origHeight(self):
        return self._origHeight
    def largeKey(self):
        return self._largeKey
    def largeWidth(self):
        return self._largeWidth
    def largeHeight(self):
        return self._largeHeight
    def mediumKey(self):
        return self._mediumKey
    def mediumWidth(self):
        return self._mediumWidth
    def mediumHeight(self):
        return self._mediumHeight
    def smallKey(self):
        return self._smallKey
    def smallWidth(self):
        return self._smallWidth
    def smallHeight(self):
        return self._smallHeight



#
# ProfilePicture: handles upload of profile picture (including resizing)
#
# Input: Takes a file pointer of file that is uploaded
# 
# uploadToS3() does upload and passes back url or None
#
# TODO: work on refactoring to reduce code duplication later
#
class ProfilePicture:
    def __init__(self, file):
        self._fp = file

    def filePointer(self):
        return self._fp

    # This sanitizes the filename for security purposes
    def filename(self):
        return secure_filename(self.filePointer().filename)

    def isImage(self):
        ext = fileExt(self.filename())
        if ext and ext in IMAGE_TYPES.keys():
            return True
        return False 

    def uploadToS3(self, userId):
        if not file or not self.isImage():
            return None

        tempFile = "tmp/TmpProfile-" + str(userId)
        tempResizedFile = "tmp/TmpResized-" + str(userId)
        self.filePointer().save(tempFile)

        # ensure image is valid
        image = Image.open(tempFile)
        if not image:
            # Error: not recognized as image
            return None

        origWidth, origHeight = image.size
        if origWidth <= 0 or origHeight <= 0:
            # Error image with 0 dimension isn't really an image
            return None

        # PIL supports several image modes. We want them in RGB
        if image.mode != "RGB":
            image.convert("RGB")

        # Resize image as necessary
        #
        # For simplicity and performance, use the same image and
        # continually downsize it.
        #
        # If performance is a problem, we might want to downsize with lowest
        # fidelity beforehand as described here:
        #
        # http://stackoverflow.com/questions/273946/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
        #
        width = origWidth
        height = origHeight
        if width != height and \
           width != PROFILE_PICTURE_WIDTH:
            if width > height:
                x1 = 0
                y1 = 0
                x2 = width
                y2 = height
                x1 = int((x2/2) - floor(float(y2)/float(2)))
                x2 = int((x2/2) + ceil(float(y2)/float(2)))
                image = image.crop((x1,y1,x2,y2))
            else:
                x1 = 0
                y1 = 0
                x2 = width
                y2 = height
                y1 = int((y2/2) - floor(float(x2)/float(2)))
                y2 = int((y2/2) + ceil(float(x2)/float(2)))
                image = image.crop((x1,y1,x2,y2))
        width = PROFILE_PICTURE_WIDTH
        height = PROFILE_PICTURE_WIDTH
        image.thumbnail((width, height), Image.ANTIALIAS)
        image.save(tempResizedFile, format='JPEG')

        # upload to S3
        keyName = "profile_picture/" + str(userId) + "/profile.jpg"

        s3Bucket = S3_CONN.get_bucket(S3_BUCKET_NAME)
        s3Key = Key(s3Bucket)
        s3Key.key = keyName

        headers = {'Content-Type' : contentType(self.filename()) }

        try:
            s3Key.set_contents_from_filename(tempResizedFile, headers)
        except:
            return None

        os.remove(tempFile)
        os.remove(tempResizedFile)

        return S3_HTTPS_HEADER + S3_BUCKET_NAME + "/" + keyName

#
# ImageFilePreview : handles manual upload of files to a preview image on S3
#
# Input: Takes a file pointer of file that is uploaded
# 
# uploadForPreview() does the upload to S3 and passes back
# a url to the preview
#
class ImageFilePreview:

    def __init__(self, file):
        self._fp = file

    def filePointer(self):
        return self._fp

    # This sanitizes the filename for security purposes
    def filename(self):
        return secure_filename(self.filePointer().filename)

    def isImage(self):
        ext = fileExt(self.filename())
        if ext and ext in IMAGE_TYPES.keys():
            return True
        return False 

    def uploadForPreview(self, userId):
        keyName = "preview/" + str(userId) + "/Preview." + fileExt(self.filename())

        s3Bucket = S3_CONN.get_bucket(S3_BUCKET_NAME)
        s3Key = Key(s3Bucket)
        s3Key.key = keyName

        headers = {'Content-Type' : contentType(self.filename()) }

        numBytes = s3Key.set_contents_from_file(self.filePointer(), headers)
        if numBytes > 0:
            return S3_HTTPS_HEADER + S3_BUCKET_NAME + "/" + keyName
        return None

#
# ImageUrlUpload
#
# Class to handle pictures for a vision.
#
# Input: URL of file (may be a preview or url from elsewhere on the web)
#
# saveAsVisionImage() saves to S3 as the different sizes necessary
#
class ImageUrlUpload:
    def __init__(self, url):
        assert Verifier.urlValid(url), "Invalid url string"
        self._url = url

    def url(self):
        return self._url
    
    def saveAsVisionImage(self, userId):
        # get URL image
        baseFileName = "tmp/Tmp-" + str(userId)
        downloadTmpFile = baseFileName + "_d"
        imagefile = open(downloadTmpFile, 'wb')  # 'wb' for write binary
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, self.url())
        curl.setopt(pycurl.WRITEFUNCTION, imagefile.write)
        curl.setopt(pycurl.MAXFILESIZE, GET_URL_MAX_FILE_SIZE)
        curl.setopt(pycurl.CONNECTTIMEOUT, GET_URL_CONNECT_TIMEOUT)
        curl.setopt(pycurl.TIMEOUT, GET_URL_TIMEOUT)
        curl.setopt(pycurl.FAILONERROR, True)
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.setopt(pycurl.MAXREDIRS, GET_URL_MAX_REDIRECTS)
        curl.setopt(pycurl.HTTPGET, 1)
        curl.perform()
        imagefile.close()

        # ensure image is valid
        image = Image.open(downloadTmpFile)
        if not image:
            # Error: not recognized as image
            return None

        origWidth, origHeight = image.size
        if origWidth <= 0 or origHeight <= 0:
            # Error image with 0 dimension isn't really an image
            return None

        # PIL supports several image modes. We want them in RGB
        if image.mode != "RGB":
            image.convert("RGB")

        # first save the original
        origTmpFile = baseFileName + "_o.jpg"
        image.save(origTmpFile, format='JPEG')

        # Resize image as necessary
        #
        # For simplicity and performance, use the same image and
        # continually downsize it.
        #
        # If performance is a problem, we might want to downsize with lowest
        # fidelity beforehand as described here:
        #
        # http://stackoverflow.com/questions/273946/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
        #
        ratio = float(origHeight) / float(origWidth)
        largeTmpFile = baseFileName + "_l.jpg"
        mediumTmpFile = baseFileName + "_m.jpg"
        smallTmpFile = baseFileName + "_s.jpg"

        # Resize large file in necessary
        largeWidth = origWidth
        largeHeight = origHeight
        if largeWidth > VISION_LARGE_WIDTH:
            largeWidth = VISION_LARGE_WIDTH
            largeHeight = int(floor(ratio * VISION_LARGE_WIDTH))
            image.thumbnail((largeWidth, largeHeight), Image.ANTIALIAS)
        image.save(largeTmpFile, format='JPEG')

        # Resize medium file if necessary
        mediumWidth = largeWidth
        mediumHeight = largeHeight
        if mediumWidth > VISION_MEDIUM_WIDTH:
            mediumWidth = VISION_MEDIUM_WIDTH
            mediumHeight = int(floor(ratio * VISION_MEDIUM_WIDTH))
            image.thumbnail((mediumWidth, mediumHeight), Image.ANTIALIAS)
        image.save(mediumTmpFile, format='JPEG')

        # Resize small file. Also want a square thumbnail so do calculation.
        smallWidth = mediumWidth
        smallHeight = mediumHeight
        if smallWidth != smallHeight and \
           smallWidth != VISION_SMALL_WIDTH:
            if smallWidth > smallHeight:
                x1 = 0
                y1 = 0
                x2 = smallWidth
                y2 = smallHeight
                x1 = int((x2/2) - floor(float(y2)/float(2)))
                x2 = int((x2/2) + ceil(float(y2)/float(2)))
                image = image.crop((x1,y1,x2,y2))
            else:
                x1 = 0
                y1 = 0
                x2 = smallWidth
                y2 = smallHeight
                y1 = int((y2/2) - floor(float(x2)/float(2)))
                y2 = int((y2/2) + ceil(float(x2)/float(2)))
                image = image.crop((x1,y1,x2,y2))
        smallWidth = VISION_SMALL_WIDTH
        smallHeight = VISION_SMALL_WIDTH
        image.thumbnail((smallWidth, smallHeight), Image.ANTIALIAS)
        image.save(smallTmpFile, format='JPEG')

        # Create key names for S3
        # MD5 w/ time for unique number, and XOR as simple way to hide userId
        t = str(calendar.timegm(datetime.datetime.utcnow().timetuple()))
        md5 = hashlib.md5()
        md5.update(t)
        uniqueTimeString = md5.hexdigest()
        
        uniqueString = str(userId) + "_" + uniqueTimeString

        keyBase = "visions/%s/%s" % (uniqueUserString, uniqueTimeString)
        keyOrigName   = keyBase + "_o.jpg"
        keyLargeName  = keyBase + "_l.jpg"
        keyMediumName = keyBase + "_m.jpg"
        keySmallName  = keyBase + "_s.jpg"

        # Upload to S3
        s3Bucket = S3_CONN.get_bucket(S3_BUCKET_NAME)
        s3KeyOrig = Key(s3Bucket)
        s3KeyOrig.key = keyOrigName
        s3KeyLarge = Key(s3Bucket)
        s3KeyLarge.key = keyLargeName
        s3KeyMedium = Key(s3Bucket)
        s3KeyMedium.key = keyMediumName
        s3KeySmall = Key(s3Bucket)
        s3KeySmall.key = keySmallName
        headers = {'Content-Type' : 'image/jpeg'}

        try:
            s3KeyOrig.set_contents_from_filename(origTmpFile, headers)
            s3KeyLarge.set_contents_from_filename(largeTmpFile, headers)
            s3KeyMedium.set_contents_from_filename(mediumTmpFile, headers)
            s3KeySmall.set_contents_from_filename(smallTmpFile, headers)
        except:
            return None

        # Clean up tmp files
        os.remove(downloadTmpFile)
        os.remove(origTmpFile)
        os.remove(largeTmpFile)
        os.remove(mediumTmpFile)
        os.remove(smallTmpFile)

        return S3Vision(S3_BUCKET_NAME,
                        keyOrigName, origWidth, origHeight,
                        keyLargeName, largeWidth, largeHeight,
                        keyMediumName, mediumWidth, mediumHeight,
                        keySmallName, smallWidth, smallHeight)

# $eof
