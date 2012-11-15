#
# SessionManager
#
# To keep track of session-related stuff in Flask
#

from flask import session

class SessionManager:
   
    @staticmethod
    def userLoggedIn():
        assert SessionManager.__inSession(), "Not in Flask session"
        return 'user' in session

    @staticmethod
    def addUser(user):
        assert SessionManager.__inSession(), "Not in Flask session"
        session['user'] = {
            'id'        : user.id,
            'firstName' : user.firstName,
            'lastName'  : user.lastName,
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
    def __inSession():
        try:
            if session.__class__.__name__ == 'LocalProxy':
                return True
        except:
            pass
        return False

# $eof
