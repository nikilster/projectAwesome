'''
	Generate Test Data
'''
import sys

from awesome import *

from TestApi import TestApi

if app.config['LOCAL_DB'] == False:
    print "*** Don't mess with production DB!!! ***"
    sys.exit(1)

ctx = app.test_request_context()
ctx.push()

dataGenerator = TestApi()
dataGenerator.addTestData()

ctx.pop()

