'''
    Static Constants
    (Class Structured) 
'''

class Constant:
    INVALID_OBJECT_ID = -1

    LOCAL_IMAGE_DIR = 'awesome/static/tmp_image'
    
    #For Bookmarklet
    #For sending from Bookmarklet -> Create.html
    BOOKMARKLET_MEDIA_URL_KEY = "mediaUrl"
    BOOKMARKLET_MEDIA_DESCRIPTION_KEY = "mediaDescription"
    BOOKMARKLET_PAGE_URL_KEY = "pageUrl" 
    BOOKMARKLET_PAGE_TITLE_KEY = "pageTitle"


    #Posting to route "create"
    #Why do we not use Constant here? (Constant.BOOKMARKLET_MEDIA_URL_KEY)
    BOOKMARKLET_POST_MEDIA_URL  = BOOKMARKLET_MEDIA_URL_KEY
    BOOKMARKLET_POST_TEXT       = "text"
    BOOKMARKLET_POST_PAGE_URL   = BOOKMARKLET_PAGE_URL_KEY
    BOOKMARKLET_POST_PAGE_TITLE = BOOKMARKLET_PAGE_TITLE_KEY
    BOOKMARKLET_POST_IS_PRIVATE = "private"

    #DB Schema (For translating db models)
    USER_FIRST_NAME             = "firstName"

    #For Email
    EMAIL_TO_KEY                = "to"
    EMAIL_SUBJECT_KEY           = "subject"
    EMAIL_BODY_HTML_KEY         = "HTMLBody"
    EMAIL_BODY_TEXT_KEY         = "textBody"