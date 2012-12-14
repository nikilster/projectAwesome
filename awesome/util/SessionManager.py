#
# SessionManager
#
# To keep track of session-related stuff in Flask
#
import os
from flask import session

from Verifier import Verifier

class SessionManager:
   
    @staticmethod
    def userLoggedIn():
        assert SessionManager.__inSession(), "Not in Flask session"
        return 'user' in session

    @staticmethod
    def setUser(user):
        assert SessionManager.__inSession(), "Not in Flask session"
        session['user'] = {
            'id'        : user.id(),
            'firstName' : user.firstName(),
            'lastName'  : user.lastName(),
            'email'     : user.email(),
            'picture'   : user.picture(),
            'description' : user.description(),
            'visionPrivacy' : user.visionPrivacy(),
        }

    @staticmethod
    def getUser():
        assert SessionManager.__inSession(), "Not in Flask session"
        assert SessionManager.userLoggedIn(), "User should be logged in"
        return session['user']

    @staticmethod
    def removeUser():
        assert SessionManager.__inSession(), "Not in Flask session"
        session.pop('user', None)

    @staticmethod
    def setPreviewUrl(url):
        assert SessionManager.__inSession(), "Not in Flask session"
        assert Verifier.urlValid(url), "Invalid preview url"
        session['previewUrl'] = url

    @staticmethod
    def getPreviewUrl():
        assert 'previewUrl' in session, "Preloaded image not there"
        url = session['previewUrl']
        assert Verifier.urlValid(url), "Invalid preview url"
        return url

    @staticmethod
    def setSelectedVisions(text):
        assert SessionManager.__inSession(), "Not in Flask session"
        session['selectedVisions'] = text

    # Returns list of vision ids that were selected if the data is valid
    @staticmethod
    def getSelectedVisions():
        assert SessionManager.__inSession(), "Not in Flask session"
        if 'selectedVisions' in session:
            data = None
            try:
                data = json.loads(session['selectedVisions'])
            except:
                pass
            if data != None and isinstance(data, list):
                ok = True
                for item in data:
                    if not isinstance(item, int):
                        ok = False
                        break
                if True == ok:
                    return data
        return None

    @staticmethod
    def removeSelectedVisions():
        assert SessionManager.__inSession(), "Not in Flask session"
        if 'selectedVisions' in session:
            session.pop('selectedVisions', None)

    @staticmethod
    def __inSession():
        try:
            if session.__class__.__name__ == 'LocalProxy':
                return True
        except:
            pass
        return False

# $eof
