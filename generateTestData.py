'''
	Generate Test Data
'''
from awesome import *

from TestApi import TestApi

ctx = app.test_request_context()
ctx.push()

dataGenerator = TestApi()
dataGenerator.addTestData()

ctx.pop()

