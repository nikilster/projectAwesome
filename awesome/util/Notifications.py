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
from awesome.api.VisionComment import VisionComment
from awesome.api.Picture import Picture

import random

class Notifications:
    
    TEST = True
    TEST_EMAIL_ADDRESS = "alex.shye@gmail.com"

    class UserKey:
        RANDOM_VISION = 'randomVision'

    def __init__(self, test=True):
        self.TEST = test

    def sendDailyEmails(self):
        ''' Send daily motivational emails, and return number of emails sent '''
        #Get motivatinal picture for each user
        userInfo = self.__getMotivationContent()

        #Render Templates
        emailInfo = self.__generateEmails(userInfo)

        #Send Email
        emailer = Emailer()
        emailer.sendBatch(emailInfo)

        #Write to log

        return len(emailInfo)

    def testDailyEmail(self):
        #Get motivatinal picture for each user
        userInfo = self.__getMotivationContent()

        #Render Templates
        emailInfo = self.__generateEmails(userInfo)

        return emailInfo[0][Constant.EMAIL_BODY_HTML_KEY]

    def testWelcomeEmail(self, user):
        return render_template("email/welcome.html", user = user)

    def sendWelcomeEmail(self, user):
        '''Takes dictionaries as input'''
        emailAddress = user[User.Key.EMAIL]
        emailSubject = "Welcome to Project Awesome!"
        emailText = emailSubject
        emailHtml = render_template("email/welcome.html", user=user)
        email = {
            Constant.EMAIL_TO_KEY : emailAddress,
            Constant.EMAIL_SUBJECT_KEY : emailSubject,
            Constant.EMAIL_BODY_TEXT_KEY : emailText,
            Constant.EMAIL_BODY_HTML_KEY : emailHtml,
        }
        emailer = Emailer()
        emailer.sendBatch([email])

    # These emails only work in production right now
    # TODO: need better way of testing these things
    def sendRepostEmail(self, user, origVision, newVision):
        '''Takes dictionaries as input'''
        origUser = User.getById(origVision['userId'])
        if origUser:
            origUser = origUser.toDictionaryFull()

            emailAddress = origUser[User.Key.EMAIL]
            emailSubject = user[User.Key.FULL_NAME] + " reposted your vision"
            emailText = emailSubject
            emailHtml = render_template("email/repost.html",
                                        origUser = origUser,
                                        origVision = origVision,
                                        user = user,
                                        vision = newVision)
            email = {
                Constant.EMAIL_TO_KEY : emailAddress,
                Constant.EMAIL_SUBJECT_KEY : emailSubject,
                Constant.EMAIL_BODY_TEXT_KEY : emailText,
                Constant.EMAIL_BODY_HTML_KEY : emailHtml,
            }
            emailer = Emailer()
            emailer.sendBatch([email])


    # These emails only work in production right now
    # TODO: need better way of testing these things

    def sendCommentEmail(self, authorUser, vision, comment):
        '''Takes dictionary inputs'''
        visionUser = User.getById(vision[Vision.Key.USER_ID])
        if visionUser:
            visionUser = visionUser.toDictionaryFull()
            emailAddress = visionUser[User.Key.EMAIL]
            emailSubject = authorUser[User.Key.FULL_NAME] + " wrote on your vision"
            emailText = emailSubject
            emailHtml = render_template("email/comment.html", 
                                        author = authorUser,
                                        user = visionUser,
                                        vision = vision,
                                        comment = comment)
            email = {
                Constant.EMAIL_TO_KEY : emailAddress,
                Constant.EMAIL_SUBJECT_KEY : emailSubject,
                Constant.EMAIL_BODY_TEXT_KEY : emailText,
                Constant.EMAIL_BODY_HTML_KEY : emailHtml,
            }
            emailer = Emailer()
            emailer.sendBatch([email])

    # These emails only work in production right now
    # TODO: need better way of testing these things
    def sendCommentNotificationEmail(self, userToEmail, authorUser,
                                           vision, comment):
        '''Takes dictionary inputs'''
        visionUser = User.getById(vision[Vision.Key.USER_ID])
        if visionUser:
            visionUser = visionUser.toDictionary()
            emailAddress = userToEmail[User.Key.EMAIL]
            if authorUser[User.Key.ID] == visionUser[User.Key.ID]:
                emailSubject = authorUser[User.Key.FULL_NAME] + \
                                " responded on their vision"
            else:
                emailSubject = authorUser[User.Key.FULL_NAME] + \
                               " responded on " + \
                               visionUser[User.Key.FULL_NAME] + "\'s vision"
            emailText = emailSubject
            emailHtml = render_template("email/commentNotification.html",
                                        userToEmail=userToEmail,
                                        authorUser=authorUser,
                                        visionUser=visionUser,
                                        vision=vision,
                                        comment=comment)
            email = {
                Constant.EMAIL_TO_KEY : emailAddress,
                Constant.EMAIL_SUBJECT_KEY : emailSubject,
                Constant.EMAIL_BODY_TEXT_KEY : emailText,
                Constant.EMAIL_BODY_HTML_KEY : emailHtml,
            }
            emailer = Emailer()
            emailer.sendBatch([email])

    def sendVisionLikeEmail(self, user, liker, vision):
        '''Takes dictionary inputs'''
        emailAddress = user[User.Key.EMAIL]
        emailSubject = liker[User.Key.FULL_NAME] + " liked your vision"
        emailText = emailSubject
        emailHtml = render_template("email/vision_like.html", 
                                    user = user,
                                    liker = liker,
                                    vision = vision)
        email = {
            Constant.EMAIL_TO_KEY : emailAddress,
            Constant.EMAIL_SUBJECT_KEY : emailSubject,
            Constant.EMAIL_BODY_TEXT_KEY : emailText,
            Constant.EMAIL_BODY_HTML_KEY : emailHtml,
        }
        emailer = Emailer()
        emailer.sendBatch([email])

    def sendVisionCommentLikeEmail(self, user, liker, vision, comment):
        '''Takes dictionary inputs'''
        emailAddress = user[User.Key.EMAIL]
        emailSubject = liker[User.Key.FULL_NAME] + " liked your comment"
        emailText = emailSubject
        emailHtml = render_template("email/vision_comment_like.html", 
                                    user = user,
                                    liker = liker,
                                    vision = vision,
                                    comment = comment)
        email = {
            Constant.EMAIL_TO_KEY : emailAddress,
            Constant.EMAIL_SUBJECT_KEY : emailSubject,
            Constant.EMAIL_BODY_TEXT_KEY : emailText,
            Constant.EMAIL_BODY_HTML_KEY : emailHtml,
        }
        emailer = Emailer()
        emailer.sendBatch([email])

    def sendFollowEmail(self, follower, user):
        '''Takes dictionary inputs'''
        emailAddress = user[User.Key.EMAIL]
        emailSubject = follower[User.Key.FULL_NAME] + " is following you!"
        emailText = emailSubject
        emailHtml = render_template("email/follow.html", 
                                    follower = follower,
                                    user = user)
        email = {
            Constant.EMAIL_TO_KEY : emailAddress,
            Constant.EMAIL_SUBJECT_KEY : emailSubject,
            Constant.EMAIL_BODY_TEXT_KEY : emailText,
            Constant.EMAIL_BODY_HTML_KEY : emailHtml,
        }
        emailer = Emailer()
        emailer.sendBatch([email])


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
                visionObj = vision.toDictionary(
                                            options=[Vision.Options.PICTURE])
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
            if self.TEST:
                email[Constant.EMAIL_TO_KEY] = Notifications.TEST_EMAIL_ADDRESS
            else:
                email[Constant.EMAIL_TO_KEY] = info[User.Key.EMAIL]
           
            email[Constant.EMAIL_SUBJECT_KEY]   = self.__subject(info)
            email[Constant.EMAIL_BODY_TEXT_KEY] = self.__textEmail(info)
            email[Constant.EMAIL_BODY_HTML_KEY] = self.__HTMLEmail(info)

            emails.append(email)
            
            if self.TEST:
                break

        return emails


    #Subject of the daily email!
    def __subject(self, userInfo):
        return self.__greeting()

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
        visionBoardUrl = "http://project-awesome.herokuapp.com/user/" + str(userInfo[User.Key.ID])
        visionUrl = "http://project-awesome.herokuapp.com/vision/" + \
                    str(userInfo[Notifications.UserKey.RANDOM_VISION]\
                                [Vision.Key.ID])
        if vision:
            picture = vision[Vision.Key.PICTURE]
            visionPictureUrl = picture[Picture.Key.LARGE_URL]
        return render_template("email/daily.html", 
                    firstName = userInfo[User.Key.FIRST_NAME],
                    title = title,
                    greeting = greeting,
                    challenge = challenge,
                    farewell = farewell,
                    visionBoardUrl = visionBoardUrl,
                    visionPictureUrl = visionPictureUrl,
                    visionUrl = visionUrl,
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
                      "Cheers",
                      "Til tomorrow",
                      "Be well",
                      "Stay cool",
                      "Ciao",
                    ]
        return random.choice(farewells)

    def __challenge(self):
        challenges = [ "Any thoughts on this vision?",
                       "Comment on your vision",
                       "What's new?",
                       "Jot down your next steps",
                       "Made progress recently?",
                       "Why's this vision awesome?",
                       "Why does this vision matter?"
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
         "Bruce Lee (1940-1973, martial artist, actor, philosopher)"),
        ("The key to immortality is first living a life worth remembering.",
         "Bruce Lee (1940-1973, martial artist, actor, philosopher)"),
        ("Don't fear failure. Not failure, but low aim, is the crime. In great attempts it is glorious even to fail.",
         "Bruce Lee (1940-1973, martial artist, actor, philosopher)"),
        ("There are no limits. There are only plateaus, and you must not stay there, you must go beyond them.",
         "Bruce Lee (1940-1973, martial artist, actor, philosopher)"),
        ("I hope you live a life you're proud of. If you find you're not, I hope you have the strength to start all over again.",
         "F. Scott Fitzgerald (1896-1940, author)"),
        ("Reflect upon your present blessings - of which every man has many - not on your past misfortunes, of which all men have some.",
         "Charles Dickens (1812-1870, novelist)"),
        ("Every piece of the universe, even the tiniest snow crystal, matters somehow. I have a place in the pattern, and so do you.",
         "T.A. Barron (born 1952, writer)"),
        ("If I made it, it's half because I was game enough to take a lot of punishment along the way, and half because there were a lot of people who cared enough to help me.",
         "Althea Gibson (1927-2003, First African-American woman on world tennis tour)"),
        ("The ultimate measure of a man is not where he stands in moments of comfort and convenience, but where he stands at times of challenge and controversy.",
         "Martin Luther King, Jr. (1929-1968, minister, civil rights activitst)"),
        ("Sometimes there is nothing you can do, and in those times, you must do something anyway.",
         "Garrison Keillor (born 1942, author, radio personality)"),
        ("Sometimes you will never know the value of a moment until it becomes a memory.",
         "Theodor Seuss Geisel (1904-1991, writer, cartoonist)"),
        ("The only person you are destined to become is the person you decide to be.",
         "Ralph Waldo Emerson (1803-1882, philosopher, poet, author)"),
        ("If you have built castles in the air, your work need not be lost; that is where they should be. Now put the foundations under them.",
         "Henry David Thoreau (1817-1862, author, poet, philosopher)"),
        ("What I've experienced is that I can't know the future. I can't know if anything that I do will change what happens tomorrow. I can't know with certaintly, but what I do know is if I do nothing, nothing will change.",
         "James Orbinski (born 1960, Former President of Doctors without Borders)"),
        ("The best way to find yourself is to lose yourself in the service of others.",
         "Mohandas Karamchand Ghandi (1869-1948, political and spiritual leader)"),
        ("Well done is better than well said.",
         "Benjamin Franklin (1706-1790, author, politician, scientist)"),
        ("For last year's words belong to last year's language, and next year's words await another voice. To make an end is to make a beginning.",
         "T.S. Eliot (188-1965, poet)"),
        ("To practice any art, no matter how well or badly, is a way to make your soul grow. So do it.",
         "Kurt Vonnegut, Jr. (1922-2007, writer)"),
        ("The people who get on in this world are the people who get up and look for the circumstances they want, and, if they can't find them, make them.",
         "George Bernard Shaw (1856-1950, playwright, critic, political activist)"),
        ("I have found that if you love life, life will love you back.",
         "Arthur Rubinstein (1887-1982, pianist)"),
        ("Things turn out best for people who make the best of the way things turn out.",
         "John R. Wooden (born 1910-2010, basketball coach)"),
        ("The most effective way to do it, is to do it.",
         "Amelia Earhart (1897-1937, aviation pioneer, author)"),
        ("It is only when we truly know and understand that we have limited time on Earth and that we have no way of knowing when our time is up that we will begin to live each day to the fullest, as if it were the only one we had.",
         "Elisabeth Kubler-Ross (1926-2004, psychiatrist, author)"),
        ("If you obey all the rules, you miss all the fun.",
         "Katharine Hepburn (1907-2003, actress)"),
        ("Life is not measured by the number of breaths we take, but by the moments that take our breath away.",
         "Maya Angelou (born 1928, author, poet)"),
        ("Everyone has inside of her a piece of good news. The good news is that you don't know how great you can be! How much you can love! What you can accomplish! And what your potential is!",
         "Anne Frank (1929-1945, author of widely-read diary)"),
        ("The future belongs to those who believe in the beauty of their dreams.",
         "Eleanor Roosevelt (1884-1962, first lady)"),
        ("We can do no great things, only small things with great love.",
         "Mother Teresa (1910-1997, founder of Missionaries of Charity)"),
        ("When I stand before God at the end of my life, I would hope that I would not have a single bit of talent left, and could say\"I used everything you gave me\".",
         "Erma Louise Bombeck (1927-1996, columnist, writer)"),
        ("Always go with the choice that scares you the most, because that's the one that is going to require the most from you.",
         "Caroline Myss (born 1952, author)"),
        ("You take your life in your own hands, and what happens? A terrible thing. No one to blame.",
         "Erica Jong (born 1942, author, teacher)"),
        ("And the trouble is, if you don't risk anything, you risk more.",
         "Erica Jong (born 1942, author, teacher)"),
        ("Stop wearing your wishbone where your backbone ought to be.",
         "Elizabeth Gilbert (born 1969, author)"),
        ("I'm not afraid of storms, for I'm learning to sail my ship.",
         "Louisa May Alcott (1832-1888, novelist)"),
        ]
        return random.choice(quotes)

# $eof
