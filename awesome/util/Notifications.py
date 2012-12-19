'''
    Notifications

    Handles

    Use this to create email templates: http://beaker.mailchimp.com/inline-css
'''
from flask import render_template
from Emailer import Emailer
from ..Constant import Constant
from Logger import Logger
from awesome.api.User import User
from awesome.api.Vision import Vision
from awesome.api.Picture import Picture

import random

class Notifications:
    
    TEST = True
    TEST_EMAIL_ADDRESS = "alex.shye@gmail.com"

    class UserKey:
        RANDOM_VISION = 'randomVision'

    #USER_EMAIL = 'email'
    #USER_FIRST_NAME = 'firstName'
    #USER_LAST_NAME = 'lastName'
    #USER_ID = 'userId'
    #USER_PICTURE_URL = "motivationUrl"


    def __init__(self, test=True):
        self.TEST = test

    '''
        Send Motivational Emails Daily
    '''
    def sendDailyEmails(self):
        
        #Get motivatinal picture for each user
        userInfo = self.__getMotivationContent()

        '''
        for user in userInfo:
            print str(user[User.Key.FIRST_NAME]) + " " + \
                  str(user[User.Key.LAST_NAME]) + \
                  "  --  " + str(user[Notifications.UserKey.RANDOM_VISION])
        '''

        #Render Templates
        emailInfo = self.__generateEmails(userInfo)

        #Send Email
        emailer = Emailer()
        emailer.sendBatch(emailInfo)

        #Write to log


    def sendWelcomeEmail(self):
        pass

    def sendRepinEmail(self):
        pass

    def sendFollowEmail(self):
        pass



    #
    #   Helper Functions
    # 
    #Get Data
    def __getMotivationContent(self):
        users = User.getAllUsers()
        data = []
        for user in users:
            obj = user.toDictionaryFull()
            vision = user.randomVision()
            if vision:
                visionObj = vision.toDictionaryDeep()
                obj[Notifications.UserKey.RANDOM_VISION] = visionObj
                data.append(obj)
            else:
                # For now, ignore users without any visions
                # !!!!! FIX THIS LATER SINCE WE SHOULD SEND THEM SOMETHING !!!!
                #obj[Notifications.UserKey.RANDOM_VISION] = None
                pass
        return data

        ''' 
        #Get the info
        userInfo = DataApi.getUsersAndRandomVision()

        #Format
        users = []
        for info in userInfo:

            Logger.debug(info)
            userData = info[0]
            visionData = info[1]

            #User Info
            user = {}
            user['id'] = userData.id
            user['firstName'] = userData.firstName
            user['lastName'] = userData.lastName
            user['email'] = userData.email

            #Vision Info
            vision = {}
            vision['text'] = visionData['text']
            vision['id'] = visionData['id']
            vision['pictureId'] = visionData['picture']['id']
            vision[Notifications.USER_PICTURE_URL] = visionData['picture']['original']

            #Add vision to user
            user['vision'] = vision
                
            #Add to list
            users.append(user)

            Logger.debug(user)

        return users
        '''
    
    #Generate the Daily Emails  
    def __generateEmails(self, emailInfo):

        emails = []

        #Create the Emails
        for info in emailInfo:
            
            email = {}
            if(Notifications.TEST):
                email[Constant.EMAIL_TO_KEY] = Notifications.TEST_EMAIL_ADDRESS
            else:
                email[Constant.EMAIL_TO_KEY] = info[User.Key.EMAIL]
           
            email[Constant.EMAIL_SUBJECT_KEY]   = self.__subject(info)
            email[Constant.EMAIL_BODY_TEXT_KEY] = self.__textEmail(info)
            email[Constant.EMAIL_BODY_HTML_KEY] = self.__HTMLEmail(info)

            emails.append(email)
            
            if(Notifications.TEST):
                break

        return emails


    #Subject of the daily email!
    def __subject(self, userInfo):

        return "You can do it!"

    def __textEmail(self, userInfo):

        return "Hi " + userInfo[User.Key.FIRST_NAME] + "!"

    def __HTMLEmail(self, userInfo):
        
        title = "Motivation for " + userInfo[User.Key.FIRST_NAME]
        motivation = self.__motivation()
        (quote, quoteAttribution) = self.__quote()

        vision = userInfo[Notifications.UserKey.RANDOM_VISION]
        pictureUrl = ""
        if vision:
            picture = vision[Vision.Key.PICTURE]
            pictureUrl = picture[Picture.Key.LARGE_URL]
        return render_template("email/dailyInlined.html", 
                    firstName = userInfo[User.Key.FIRST_NAME],
                    title = title,
                    motivation = motivation,
                    pictureUrl = pictureUrl,
                    quote = quote,
                    quoteAttribution = quoteAttribution)


    def __motivation(self):
        motivation = [ "You can do it!", "Have a great day!"]
        return random.choice(motivation)


    def __quote(self):
        quotes = [("Life has many ways of testing a person's will, either by having nothing happen at all or by having everything happen all at once.", "Paulo Coelho (poet, writer - born 1947)"),\
                    ("As we express our gratitude, we must never forget that the highest appreciation is not to utter words, but to live by them.", "John F. Kennedy (1917-1963, 35th US President")]
        return random.choice(quotes)
