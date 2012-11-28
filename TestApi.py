'''
    Load Test Data with API

    Wipes Database
'''

#Add the api.py (parent) folder
import os
import sys

from awesome.api.Api import Api

import random

class TestApi:

    #Erase all of the data from the database (for the test phase)
    CLEAR_DATA = True
    NUM_USERS = 2
    NUM_VISIONS = 10

    #Users
    firstNames = ["Nikil", "Alex", "Aditya", "Jason", "Chris"]
    lastNames = ["Viswanathan", "Shye", "Mantha", "Ford", "Piech"]
    password = "awesome"
    email = "nikil@stanford.edu"

    #Visions
    texts = ["I'm pretty sure there's a lot more to life than being really, really, ridiculously good looking. And I plan on finding out what that is.", \
            "He's so hot right now! ", \
            "How can we be expected to teach children to learn how to read if they can't even fit inside the building?", \
            "I turned left!"]

    pictures = ['http://mollypiper.com/wp-content/uploads/2011/02/zoolander.jpg', \
                'http://bluesuedeshoes.files.wordpress.com/2010/03/13zoolander.jpg', \
                'http://www.geekosystem.com/wp-content/uploads/2011/01/zoolander.jpg', \
                'http://t0.gstatic.com/images?q=tbn:ANd9GcSd61qC_S8cVn1biniVS4Sbppdc-xGx-eqNo8k1M86C3idBAN_gHc2h9CEg3g']

    #TODO: picture deduplication -url hashing 

    #picture filename
    pictureFilename = "1"

    #repost
    parentId = 0




    '''
        Add Test Data
            Clear data (optional)
            Add
    '''
    def addTestData(self):

        print "\n\n"
        print "-------------------------------"
        print "Creating Test Data"
        print "Clearing the current database!"
        print "Adding " + str(TestApi.NUM_USERS) + " Users"
        print "Adding " + str(TestApi.NUM_VISIONS) + " Per User"
        print "-------------------------------"
        print "\n"

        #if(TestApi.CLEAR_DATA):
        #   self.clearData()

        self.addUsers(TestApi.NUM_USERS)

    '''
    def clearData(self):
        db = DB()
        db._DB__secretClean()
    '''

    '''
        Add Users
            Random Field Users
    '''
    def addUsers(self, numUsersToAdd):

        for i in range(0,numUsersToAdd):
            firstName = random.choice(TestApi.firstNames)
            lastName = random.choice(TestApi.lastNames)
            email = "TEST" + str(i) + "-" + TestApi.email
            password = TestApi.password

            #Add
            (userId, msg)= Api.registerUser(firstName, lastName,
                                            email, password)
            if(userId == -1):
                print "Error adding user: " + firstName + " " + lastName + " " + email
                print "Skiping adding visions for: " + firstName
                continue

            print "Added user: " + firstName + " " + lastName + " " + email
            self.addVisions(userId, TestApi.NUM_VISIONS)
            print "Added " + str(TestApi.NUM_VISIONS) + " visions for " + firstName + "\n"



    '''
        Add Visions 
            For User
    '''
    def addVisions(self, userId, numVisionsToAdd):

        for i in range(0, numVisionsToAdd):
            text = random.choice(TestApi.texts)
            url = random.choice(TestApi.pictures)

            #Add
            Api.saveVision(userId, url, text, "", "")


