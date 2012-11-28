#
# Logger.py - Utility class for debug logging in Flask
#
# Note: only works with app.config['DEBUG'] == True
#

from .. import app


class Logger:
    @staticmethod
    def info(str):
        app.logger.info(str)

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
