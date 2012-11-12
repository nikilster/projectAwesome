from User import User
from Vision import Vision

u = User()
u.setFromJson('{"password": "as", "id": 1, "email": "nikilster@gmail.com"}')
print u.email
print u.dateCreated

v = Vision()
v.setFromJson('{"id":1, "userId": 1}')
print v.id
print v.userId