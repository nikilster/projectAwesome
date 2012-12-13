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

class Notifications:
    
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
        #emailer.sendBatch(emailInfo)

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
        
        userInfo = Api.getEmailContent()

        users = {}
        for info in userInfo:
            userData = userInfo[0]
            visionData = userInfo[1]

            userId = Constant.USER_FIRST_NAME
            Logger.debug(info[0][] + " " + info[0].email + " " + info[1]['picture']['mediumUrl'])
            
        return userInfo
    
    #Generate the Daily Emails  
    def __generateEmails(self, userInfo):

        emails = []

        #Create the Emails
        for info in userInfo:
            
            email = {}
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
        
        title = "Motivation for Nikil "
        motivation = "You CAN do it!"
        quote = "Life has many ways of testing a person's will, either by having nothing happen at all or by having everything happen all at once."
        quoteAttribution = "Paulo Coelho (poet, writer - born 1947)"
        return render_template("email/dailyInlined.html", 
                    firstName = userInfo[Notifications.USER_FIRST_NAME],
                    title = title,
                    motivation = motivation,
                    pictureUrl = userInfo[Notifications.USER_PICTURE_URL],
                    quote = quote,
                    quoteAttribution = quoteAttribution)


