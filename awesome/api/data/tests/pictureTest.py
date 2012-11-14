'''
	pictureTest.py

'''

#Add the api.py (parent) folder
import sys
sys.path.append("../objects")

from Picture import Picture
from Vision import Vision

v = Vision()
v.setInfo(1,1,"hi!", 2, 0, '12312312323')

p = Picture()
#filename is the name of the file on the web server
p.setInfo(1,'www.facebook.com/hi.jpg', '1')

v.setPicture(p)

print(v.toDictionary())