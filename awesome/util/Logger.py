#
# Logger.py - Utility class for debug logging in Flask
#

from .. import APP


class Logger:
    @staticmethod
    def debug(str):
        APP.logger.debug(str)

    @staticmethod
    def warning(str):
        APP.logger.warning(str)

    @staticmethod
    def error(str):
        APP.logger.error(str)

###############################################################################
# $eof
