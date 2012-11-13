from .. import APP

#
# Debugging
#

def logD(str):
  APP.logger.debug(str)
def logW(str):
  APP.logger.warning(str)
def logE(str):
  APP.logger.error(str)

