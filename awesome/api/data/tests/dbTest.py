'''
	Db Test
'''

#Add the db.py (parent) folder
import sys
sys.path.append("../")

from DB import DB


db = DB()
print(db.getUserFromEmail("nikil@stanford.edu"))
print(db.getUserFromEmail("nikilster@gmail.com"))