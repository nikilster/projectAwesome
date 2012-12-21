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

    def testDailyEmail(self):
        #Get motivatinal picture for each user
        userInfo = self.__getMotivationContent()

        #Render Templates
        emailInfo = self.__generateEmails(userInfo)

        return emailInfo[0][Constant.EMAIL_BODY_HTML_KEY]

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
        greeting = self.__greeting()
        farewell = self.__farewell()
        challenge = self.__challenge()
        (quote, quoteAttribution) = self.__quote()

        vision = userInfo[Notifications.UserKey.RANDOM_VISION]
        visionText = vision[Vision.Key.TEXT]
        visionPictureUrl = ""
        if vision:
            picture = vision[Vision.Key.PICTURE]
            visionPictureUrl = picture[Picture.Key.LARGE_URL]
        return render_template("email/daily.html", 
                    firstName = userInfo[User.Key.FIRST_NAME],
                    title = title,
                    greeting = greeting,
                    challenge = challenge,
                    farewell = farewell,
                    visionPictureUrl = visionPictureUrl,
                    visionText = visionText,
                    quote = quote,
                    quoteAttribution = quoteAttribution)


    def __greeting(self):
        greetings = [ "You can do it!",
                       "Good morning!",
                       "Daily awesomeness",
                       "With love, from us to you.",
                       "Let's go!",
                       "Hey there, good looking ;)",
                       "How's it going?",
                       "Daily zen",
                       "Hello :)",
                       "What's up?",
                       "You had me at \"hello\"",
                     ]
        return random.choice(greetings)

    def __farewell(self):
        # We tack a comma onto these for now.. so leave empty at end.
        farewells = [ "Have an awesome day",
                      "Have a great day",
                      "Bye bye",
                      "Til tomorrow",
                      "Sayanora",
                      "Hasta la vista, baby",
                      "Adios",
                      "Be well, fellow citizen"
                      "Stay cool",
                      "And.. we're out",
                      "See ya later, alligator",
                      "C U L8R",
                      "Ciao",
                    ]
        return random.choice(farewells)

    def __challenge(self):
        challenges = [ "How are you moving towards this vision today?",
                       "What can you do today make this real?",
                       "Who should you connect with about this vision?",
                       "Where are you with this?",
                       "Why does this vision resonate with you?",
                     ]
        return random.choice(challenges)

    def __quote(self):
        quotes = [
        ("Life has many ways of testing a person's will, either by having nothing happen at all or by having everything happen all at once.",
         "Paulo Coelho (poet, writer - born 1947)"),
        ("As we express our gratitude, we must never forget that the highest appreciation is not to utter words, but to live by them.",
         "John F. Kennedy (1917-1963, 35th US President"),
        ("Make no little plans. They have no magic to stir men's blood and probably themselves will not be realized. Make big plans; aim high in hope and work, remembering that a noble, logical diagram once recorded will never die, but long after we are gone will be a living thing, asserting itself with ever-growing insistency. Remember that our sons and grandsons are going to do things that would stagger us. Let your watchword be order and your beacon beauty. Think big.",
         "Daniel Burnham (1846-1912, architect)"),
        ("You look at things and ask, why?  I dream of things that never were and ask, why not?",
         "George Bernard Shaw (1856-1950, playwright, critic, political activist)"),
        ("One should not pursue goals that are easily achieved. One must develop an instinct for what one can just barely achieve through one's greatest efforts.",
         "Albert Einstein (1879-1955, theoretical physicist)"),
        ("It is not the critic who counts; not the man who points out how the strong man stumbles, or where the doer of deeds could have done them better. The credit belongs to the man who is actually in the arena, whose face is marred by dust and sweat and blood; who strives valiantly; who errs, who comes short again and again, because there is no effort without error and shortcoming; but who does actually strive to do the deeds; who knows great enthusiasms, the great devotions; who spends himself in a worthy cause; who at the best knows in the end the triumph of high achievement, and who at the worst, if he fails, at least fails while daring greatly, so that his place shall never be with those cold and timid souls who neither know victory nor defeat.",
         "Teddy Roosevelt (1858-1919, 26th president of the U.S.)"),
        ("To accomplish great things, we must not only act, but also dream; not only plan, but also believe.",
          "Anatole France (1844-1924, poet, journalist, novelist)"),
        ("It's not whether you get knocked down, it's whether you get up.",
         "Vince Lombardi (1913-1970, American football coach)"),
        ("You can't wait for inspiration. You have to go after it with a club.",
         "Jack London (1876-1916, author, journalist, social activist)"),
        ("The question isn't who is going to let me; it's who is going to stop me",
         "Howard Roark of The Fountainhead, a novel by Ayn Rand (1905-1982, writer, philosopher)"),
        ("If you are not willing to risk the unusual, you will have to settle for the ordinary.",
         "Jim Rohn (1930-2009, entrepreneur, author, speaker)"),
        ("Those who are willing to take action and take risks succeed. The others fade quickly.",
        "Bradley Smith (born 1958, jurist, scholar)"),
        ("You've got to get up every morning with determination if you're going to go to bed with satisfaction.",
         "George Horace Lorimer (1867-1937, journalist, author)"),
        ("As you think, so shall you become.",
         "Bruce Lee (1940-1973, martial artist, actor, philosopher"),
        ("The key to immortality is first living a life worth remembering.",
         "Bruce Lee (1940-1973, martial artist, actor, philosopher"),
        ("Don't fear failure. Not failure, but low aim, is the crime. In great attempts it is glorious even to fail.",
         "Bruce Lee (1940-1973, martial artist, actor, philosopher"),
        ("I hope you live a life you're proud of. If you find you're not, I hope you have the strength to start all over again.",
         "F. Scott Fitzgerald (1896-1940, author)"),
        ]
        return random.choice(quotes)

# $eof
