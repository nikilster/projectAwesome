from . import app

from flask import Flask, current_app

from rq import Queue
from runworker import REDIS_CONN

from util.Logger import Logger

REDIS_QUEUE = Queue(connection=REDIS_CONN)

###############################################################################
# Called from Thrive web app
#
def Queue_print(string):
    REDIS_QUEUE.enqueue(Worker_print, string)

def Queue_repostEmail(user, origVision, newVision):
    REDIS_QUEUE.enqueue(Worker_repostEmail, user, origVision, newVision)

def Queue_commentEmail(authorUser, vision, comment):
    REDIS_QUEUE.enqueue(Worker_commentEmail, authorUser, vision, comment)

def Queue_commentNotificationEmail(userToEmail, authorUser, vision, comment):
    REDIS_QUEUE.enqueue(Worker_commentNotificationEmail,
                        userToEmail, authorUser, vision, comment)

def Queue_visionLikeEmail(user, liker, vision):
    REDIS_QUEUE.enqueue(Worker_visionLikeEmail, user, liker, vision)

def Queue_visionCommentLikeEmail(user, liker, vision, comment):
    REDIS_QUEUE.enqueue(Worker_visionCommentLikeEmail,
                        user, liker, vision, comment)

def Queue_followEmail(follower, user):
    REDIS_QUEUE.enqueue(Worker_followEmail, follower, user)

###############################################################################
# Worker jobs done by worker dyno
#

def Worker_print(string):
  Logger.debug(string)

from util.Notifications import Notifications

def Worker_repostEmail(user, origVision, newVision):
    ctx = app.test_request_context()
    ctx.push()

    ## WORK START ##
    notifications = Notifications(test=False)
    notifications.sendRepostEmail(user, origVision, newVision)
    ## WORK END ##

    ctx.pop()

def Worker_commentEmail(authorUser, vision, comment):
    ctx = app.test_request_context()
    ctx.push()

    ## WORK START ##
    notifications = Notifications(test=False)
    notifications.sendCommentEmail(authorUser, vision, comment)
    ## WORK END ##

    ctx.pop()

def Worker_commentNotificationEmail(userToEmail, authorUser, vision, comment):
    ctx = app.test_request_context()
    ctx.push()

    ## WORK START ##
    notifications = Notifications(test=False)
    notifications.sendCommentNotificationEmail(userToEmail, authorUser,
                                               vision, comment)
    ## WORK END ##

    ctx.pop()

def Worker_visionLikeEmail(user, liker, vision):
    ctx = app.test_request_context()
    ctx.push()

    ## WORK START ##
    notifications = Notifications(test=False)
    notifications.sendVisionLikeEmail(user, liker, vision)
    ## WORK END ##

    ctx.pop()

def Worker_visionCommentLikeEmail(user, liker, vision, comment):
    ctx = app.test_request_context()
    ctx.push()

    ## WORK START ##
    notifications = Notifications(test=False)
    notifications.sendVisionCommentLikeEmail(user, liker, vision, comment)
    ## WORK END ##

    ctx.pop()

def Worker_followEmail(follower, user):
    ctx = app.test_request_context()
    ctx.push()

    ## WORK START ##
    notifications = Notifications(test=False)
    notifications.sendFollowEmail(follower, user)
    ## WORK END ##

    ctx.pop()

# $eof
