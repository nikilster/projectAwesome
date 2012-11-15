#
# Flash messages
#

class LoginError:
    TAG = "LoginError"
    EMAIL_REQUIRED = "Email address is required"
    EMAIL_NOT_FOUND = "Email address not found"
    PASSWORD_REQUIRED = "Password is required"
    PASSWORD_INVALID = "Password is invalid"
    DB_ERROR = "Database error. Sorry, please try again!"

class RegisterError:
    TAG = "RegisterError"
    FIRST_NAME_REQUIRED = "First name is required"
    FIRST_NAME_INVALID = "First name is invalid"
    LAST_NAME_REQUIRED = "Last name is required"
    LAST_NAME_INVALID = "Last name is invalid"
    EMAIL_REQUIRED = "Email address is required"
    EMAIL_INVALID = "Email address is invalid"
    EMAIL_TAKEN = "Account already exists this email address"
    PASSWORD_REQUIRED = "Password is required"
    PASSWORD_INVALID = "Password is invalid"
    DB_ERROR = "Database error. Sorry, please try again!"

# $eof
