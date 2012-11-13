###############################################################################
#
# PasswordManager.py
#
# Uses bcrypt encryption algorithm to create hashes and verify passwords
#
###############################################################################

import bcrypt

class PasswordEncrypt:
    @staticmethod
    def genHash(password):
        return bcrypt.hashpw(password, bcrypt.gensalt())

    @staticmethod
    def verifyPassword(password, passwordHash):
        return bcrypt.hashpw(password, passwordHash) == passwordHash

###############################################################################
# $eof
