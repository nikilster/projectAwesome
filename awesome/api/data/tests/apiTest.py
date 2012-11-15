'''
	API test
'''

#Add the api.py (parent) folder
import sys
sys.path.append("../")

from DataApi import DataApi

#Test Picture
pictureId = DataApi.addPicture("www.facebook.com/hi", "1")
print "Saved Picture, got id = " + str(pictureId)
print(DataApi.getPicture(pictureId))

#Test Vision
visionId = DataApi.addVision("1", "Live Well!", pictureId, 0)
print "Saved Vision, got id = " + str(visionId)
print(DataApi.getVision(visionId))

DataApi.addUser('nikil', 'viswanthan', 'nikilster@gmail.com', 'as')
print(DataApi.getUserFromEmail('nikilster@gmail.com'))

'''
DataApi.addVision('1', 'I am awesome!!!', ':)', '1')

print(DataApi.getVision(3))


print(DataApi.getVisionsForUser(1))

visions = DataApi.getMainPageVisions()

for vision in visions:
	print vision.toDictionary()
'''