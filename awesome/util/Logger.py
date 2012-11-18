#
# Logger.py - Utility class for debug logging in Flask
#

from .. import app


class Logger:
    @staticmethod
    def debug(str):
        app.logger.debug(str)

    @staticmethod
    def warning(str):
        app.logger.warning(str)

    @staticmethod
    def error(str):
        app.logger.error(str)

###############################################################################
# $eof
