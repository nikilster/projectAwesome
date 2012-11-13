'''
	API test
'''

#Add the api.py (parent) folder
import sys
sys.path.append("../")

from DataApi import DataApi

DataApi.addUser('nikil', 'viswanthan', 'nikilster@gmail.com', 'as')
print(DataApi.getUser(1))

DataApi.addVision('1', 'I am awesome!!!', ':)', '1')

print(DataApi.getVision(3))

print(DataApi.getVisionsForUser(1))

visions = DataApi.getMainPageVisions()

for vision in visions:
	print vision.toDictionary()