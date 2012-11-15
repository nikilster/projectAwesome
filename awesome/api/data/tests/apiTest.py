'''
	API test
'''

#Add the api.py (parent) folder
import sys
sys.path.append("../")

from DataApi import DataApi

#Add User
userId = DataApi.addUser('nikil', 'viswanthan', 'nikilster@gmail.com', 'as')
print(DataApi.getUserFromEmail('nikilster@gmail.com'))

#Test Picture
pictureId = DataApi.addPicture("www.facebook.com/hi", "1")
print "Saved Picture, got id = " + str(pictureId)
print(DataApi.getPicture(pictureId))

#Test Vision
visionId = DataApi.addVision(userId, "Live Well!", pictureId, 0)
print "Saved Vision, got id = " + str(visionId)
print(DataApi.getVision(visionId))

#Test RePost
repostVisionId = DataApi.repostVision(visionId, userId)
print "Repost Vision, got id="  + str(repostVisionId)
print(DataApi.getVision(repostVisionId))


'''
DataApi.addVision('1', 'I am awesome!!!', ':)', '1')

print(DataApi.getVision(3))


print(DataApi.getVisionsForUser(1))

visions = DataApi.getMainPageVisions()

for vision in visions:
	print vision.toDictionary()
'''