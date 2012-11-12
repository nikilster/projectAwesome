'''
	API test
'''

#Add the api.py (parent) folder
import sys
sys.path.append("../")

import api

# api.addUser('nikil', 'viswanthan', 'nikilster@gmail.com', 'as')
# print(api.getUser(1))

# api.addVision('1', 'I am awesome!!!', ':)', '1')

# print(api.getVision(3))

print(api.getVisionsForUser(1))

print(api.getMainPageVisions())