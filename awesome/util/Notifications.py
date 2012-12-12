'''
    Notifications

    Handles
'''
from flask import render_template
from Emailer import Emailer
from Constant import Constant

class Notifications:
    
    USER_EMAIL = 'email'
    USER_FIRST_NAME = 'firstName'
    USER_LAST_NAME = 'lastName'
    USER_ID = 'userId'

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

        #Write to log


    def sendWelcomeEmail(self):
        pass

    def sendRepinEmail(self):
        pass

    def sendFollowEmail(self):
        pass



    '''
        Helper Functions
    ''' 
    #Get Data
    def __getMotivationContent(self):
        return {"userId":1, "firstName":"Nikil", "lastName":"Viswanathan", "email":"nikilster@gmail.com"}
    
    #Generate the Daily Emails  
    def __generateEmails(self, userInfo):

        emails = []

        #Create the Emails
        for info in userInfo:
            
            email = {}
            email[Constant.EMAIL_TO_KEY]        = userInfo[Notifications.USER_EMAIL]
            email[Constant.EMAIL_SUBJECT_KEY]   = self.__subject(userInfo)
            email[Constant.EMAIL_BODY_TEXT_KEY] = self.__textEmail(userInfo)
            email[Constant.EMAIL_BODY_HTML_KEY] = self.__HTMLEmail(userInfo)

            emails.append(email)

        return emails


    #Subject of the daily email!
    def __subject(self, userInfo):

        return "You can do it!"

    def __textEmail(self, userInfo):

        return "Hi " + userInfo[Notifications.USER_FIRST_NAME] + "!"

    def __HTMLEmail(self, userInfo):

        return render_template("email/daily.html", firstName = userInfo[Notifications.USER_FIRST_NAME])