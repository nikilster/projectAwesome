'''
    Notifications

    Handles

    Use this to create email templates: http://beaker.mailchimp.com/inline-css
'''
from flask import render_template
from Emailer import Emailer
from ..Constant import Constant
from ..api.Api import Api
from Logger import Logger
import random

class Notifications:
    
    TEST = True
    TEST_EMAIL_ADDRESS = "nikilster@gmail.com"

    USER_EMAIL = 'email'
    USER_FIRST_NAME = 'firstName'
    USER_LAST_NAME = 'lastName'
    USER_ID = 'userId'
    USER_PICTURE_URL = "motivationUrl"

    '''
        Send Motivational Emails Daily
    '''
    def sendDailyEmails(self):
        
        #Get motivatinal picture for each user
        userInfo = self.__getMotivationContent()

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
        
        #Get the info
        userInfo = Api.getEmailContent()

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
            vision[Notifications.USER_PICTURE_URL] = visionData['picture']['largeUrl']

            #Add vision to user
            user['vision'] = vision
                
            #Add to list
            users.append(user)

            Logger.debug(user)
            
        return users
    
    #Generate the Daily Emails  
    def __generateEmails(self, emailInfo):

        emails = []

        #Create the Emails
        for info in emailInfo:
            
            email = {}
            if(Notifications.TEST):
                email[Constant.EMAIL_TO_KEY] = Notifications.TEST_EMAIL_ADDRESS
            else:
                email[Constant.EMAIL_TO_KEY]        = info[Notifications.USER_EMAIL]
           
            email[Constant.EMAIL_SUBJECT_KEY]   = self.__subject(info)
            email[Constant.EMAIL_BODY_TEXT_KEY] = self.__textEmail(info)
            email[Constant.EMAIL_BODY_HTML_KEY] = self.__HTMLEmail(info)

            emails.append(email)

        return emails


    #Subject of the daily email!
    def __subject(self, userInfo):

        return "You can do it!"

    def __textEmail(self, userInfo):

        return "Hi " + userInfo[Notifications.USER_FIRST_NAME] + "!"

    def __HTMLEmail(self, userInfo):
        
        title = "Motivation for " + userInfo[Notifications.USER_FIRST_NAME]
        motivation = self.__motivation()
        (quote, quoteAttribution) = self.__quote()
        
        return render_template("email/dailyInlined.html", 
                    firstName = userInfo[Notifications.USER_FIRST_NAME],
                    title = title,
                    motivation = motivation,
                    pictureUrl = userInfo['vision'][Notifications.USER_PICTURE_URL],
                    quote = quote,
                    quoteAttribution = quoteAttribution)


    def __motivation(self):
        motivation = [ "You can do it!", "Have a great day!"]
        return random.choice(motivation)


    def __quote(self):
        quotes = [("Life has many ways of testing a person's will, either by having nothing happen at all or by having everything happen all at once.", "Paulo Coelho (poet, writer - born 1947)"),\
                    ("As we express our gratitude, we must never forget that the highest appreciation is not to utter words, but to live by them.", "John F. Kennedy (1917-1963, 35th US President")]
        return random.choice(quotes)
