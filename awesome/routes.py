from flask import render_template
from flask import abort, redirect, url_for, flash, jsonify
from flask import request, session
from flask import Response
from flask import current_app

import os
import calendar, datetime

from . import app
from Constant import Constant

from api.User import User
from api.UserList import UserList
from api.Vision import Vision
from api.VisionList import VisionList
from api.VisionLike import VisionLike
from api.VisionComment import VisionComment
from api.VisionCommentLike import VisionCommentLike
from api.FollowList import FollowList
from api.Follow import Follow
from api.Activity import Activity
from api.FlashMessages import *

from util.SessionManager import SessionManager
from util.Notifications import Notifications
from util.Logger import Logger


@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('index.html', user=userInfo, config=app.config)
        else:
            return render_template('index.html', user=None, config=app.config)
    abort(405)

@app.route('/view_board', methods=['GET'])
def view_board():
    return redirect(url_for('index'))

@app.route('/recent', methods=['GET'])
def recent():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('index.html', user=userInfo, config=app.config)
        else:
            return redirect(url_for('index'))
    abort(405)

@app.route('/user/<int:userId>', methods=['GET'])
@app.route('/user/<int:userId>/<int:pageOption>') #Page option is used to show the onboarding (= 1)
def user_profile(userId, pageOption = 0):
    
    #userId and the pageOption are set in the backbone router 
    #Just used for routing here (not as values)

    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('index.html', user=userInfo, config=app.config)
        else:
            return redirect(url_for('login', next="user", id=userId))
    abort(405)

@app.route('/vision/<int:visionId>', methods=['GET'])
def vision_page(visionId):
    if request.method == 'GET':
        userInfo = None
        visionInfo = dict()
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('index.html',
                                user=userInfo,
                                config=app.config)
        return redirect(url_for('login', next="vision", id=visionId))
    abort(405)

@app.route('/api/vision/<int:visionId>', methods=['GET'])
def apiVisionInformation(visionId):
    if request.method == 'GET':
        user = None;
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            user = User.getById(userInfo['id'])

        vision = Vision.getById(visionId, user)
        if vision:
            data = {'vision' : vision.toDictionary(
                                    options=[Vision.Options.PICTURE,
                                            Vision.Options.USER,
                                            Vision.Options.PARENT_USER,
                                            Vision.Options.LIKES],
                                    user=user)
                    }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/about', methods=['GET'])
def about():
    if request.method == 'GET':
        userInfo = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
        return render_template('about.html', user=userInfo, config=app.config)
    abort(405)

@app.route('/visualization', methods=['GET'])
def visualization():
    if request.method == 'GET':
        userInfo = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
        return render_template('visualization.html', user=userInfo, config=app.config)
    abort(405)

@app.route('/settings', methods=['GET'])
def settings():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('settings.html', user=userInfo, config=app.config)
        else:
            return render_template('index.html', user=None, config=app.config)
    abort(405)

@app.route('/api/change_info', methods=['POST'])
def api_change_info():
    if request.method == 'POST':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            if not ('firstName' in request.form or
                    'lastName' in request.form or
                    'email' in request.form or
                    'description' in request.form):
                abort(406)

            firstName = request.form['firstName']
            lastName = request.form['lastName']
            email = request.form['email']
            desc = request.form['description']
            visionPrivacy = not ('visionPrivacy' in request.form)

            user = User.getById(userInfo['id'])
            if user:
                user.setInfo(firstName, lastName, email, visionPrivacy)
                user.setDescription(desc)

                # update session
                SessionManager.setUser(user)
                userInfo = SessionManager.getUser()
            return render_template('settings.html', user=userInfo, config=app.config)
        abort(406)
    abort(405)

@app.route('/api/user/<int:userId>/set_description', methods=['POST'])
def api_user_set_description(userId):
    if request.method == 'POST':

        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            if userInfo['id'] != userId:
                abort(406)

            parameters = request.json
            if not 'description' in parameters:
                abort(406)
            description = parameters['description'].strip()

            user = User.getById(userInfo['id'])
            data = { 'result' : "error" }
            if user:
                if user.setDescription(description):
                    # update session if it worked
                    SessionManager.setUser(user)

                    data = { 'result' : "success",
                             'description' : description }
            return jsonify(data)
        abort(403)
    abort(405)
   

@app.route('/api/change_picture', methods=['POST'])
def api_change_picture():
    if request.method == 'POST':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()

            if not 'picture' in request.files:
                abort(406)
            file = request.files['picture']

            target = ""
            if 'target' in request.form:
                target = request.form['target']

            user = User.getById(userInfo['id'])
            if user:
                url = user.setProfilePicture(file)
                if url:
                    # update session if it worked
                    SessionManager.setUser(user)
            if target == "profile":
                return redirect(url_for('user_profile', userId=user.id()))
            else:
                return redirect(url_for('settings'))
        abort(406)
    abort(405)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            return redirect(url_for('index'))
        else:
            next = request.args.get('next')
            id = request.args.get('id')

            return render_template('login.html', config=app.config,
                                                 next=next,
                                                 id=id)
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        (user, errorMsg) = User.getByLogin(email, password)

        if user:
            SessionManager.setUser(user)

            nextRef = request.form.get('next')
            nextId = request.form.get('id')

            if nextRef == "vision":
                return redirect(url_for('vision_page', visionId=nextId))
            elif nextRef == "user":
                return redirect(url_for('user_profile', userId=nextId))
            else:
                return redirect(url_for('user_profile', userId=user.id()))
        else:
            assert errorMsg != None, "Error msg should exist"
            flash(errorMsg, LoginError.TAG)
            return redirect (url_for('login'))
    abort(405)

@app.route('/logout', methods=['GET'])
def logout():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            SessionManager.removeUser();
        return redirect(url_for('index'))
    abort(405)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', config=app.config)
    elif request.method == 'POST':
        # Keep selected visions in session
        if 'selectedVisions' in request.form:
            SessionManager.setSelectedVisions(
                                        str(request.form['selectedVisions']))
        return render_template('register.html', config=app.config)
    abort(405)

@app.route('/register_user', methods=['POST'])
def register_user():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        
        (user, errorMsg) = User.registerNewUser(firstName, lastName,
                                                email, password)
        if user:
            SessionManager.setUser(user)

            selectedVisionIds = SessionManager.getSelectedVisions()
            if selectedVisionIds and len(selectedVisionIds) > 0:
                #Logger.debug("Existing selected visions: " +
                #                                       str(selectedVisionIds));
                user.repostVisionList(selectedVisionIds)
                SessionManager.removeSelectedVisions()
            return redirect(url_for('user_profile', userId=user.id(), pageOption=1))
        else:
            assert errorMsg != "", "Error message should exist"
            flash(errorMsg, RegisterError.TAG)
            return redirect(url_for('register'))
    abort(405)

@app.route('/api/get_feed', methods=['GET'])
def apiUserFeed():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            user = User.getById(userInfo['id'])

            data = { 'activities' : Activity.getUserFeed(user)
                   }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/get_main_page_visions', methods=['GET'])
def apiGetMainPageVisions():
    if request.method == 'GET':
        user = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            user = User.getById(userInfo['id'])

        #mainPageVisions = VisionList.getMainPageVisions()
        mainPageVisions = Activity.getRecentVisionActivity(user)

        data = { 'otherVisions' : mainPageVisions.toDictionary(
                                        options=[Vision.Options.PICTURE,
                                                 Vision.Options.USER,
                                                 Vision.Options.PARENT_USER,
                                                 Vision.Options.COMMENTS,
                                                 Vision.Options.COMMENT_PICTURES,
                                                 Vision.Options.LIKES,
                                                 Vision.Options.COMMENT_LIKES],
                                        user=user),
                 'visionList'   : [] }

        # TODO: be smarter about when to load user vision list later
        if user:
            userVisions = VisionList.getUserVisions(user, user)
            data['visionList'] = userVisions.toDictionary()

        return jsonify(data)
    abort(405)

@app.route('/api/user/<int:targetUserId>/visions', methods=['GET'])
def apiGetUserVisions(targetUserId):
    if request.method == 'GET':
        data = {'visionList' : [],
                'otherVisions' : []
               }
        user = None
        userVisions = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            user = User.getById(userInfo['id'])
            if user:
                userVisions = VisionList.getUserVisions(user, user)
                if targetUserId == user.id():
                    data['visionList'] = userVisions.toDictionary(
                                           options=[Vision.Options.PICTURE,
                                                    Vision.Options.USER,
                                                    Vision.Options.PARENT_USER,
                                                    Vision.Options.COMMENTS,
                                                    Vision.Options.COMMENT_PICTURES,
                                                    Vision.Options.LIKES,
                                                    Vision.Options.COMMENT_LIKES],
                                           user=user)
                else:
                    data['visionList'] = userVisions.toDictionary()

        targetUser = None
        targetUserVisions = None
        if SessionManager.userLoggedIn() and targetUserId == userInfo['id']:
            targetUser = user
            targetUserVisions = userVisions
        else:
            targetUser = User.getById(targetUserId)
            if targetUser:
                targetUserVisions = VisionList.getUserVisions(user, targetUser)
        if targetUser and targetUserVisions:
            data['otherVisions'] = targetUserVisions.toDictionary(
                                        options=[Vision.Options.PICTURE,
                                                 Vision.Options.USER,
                                                 Vision.Options.PARENT_USER,
                                                 Vision.Options.COMMENTS,
                                                 Vision.Options.COMMENT_PICTURES,
                                                 Vision.Options.LIKES,
                                                 Vision.Options.COMMENT_LIKES],
                                        user=user)
            data['user'] = targetUser.toDictionary(
                                        options=[User.Options.FOLLOW_COUNTS,
                                                 User.Options.FOLLOWING],
                                        user=user);

        return jsonify(data)
    abort(405)

@app.route('/api/user/<int:userId>/move_vision', methods=['POST'])
def apiMoveUserVision(userId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():

            userInfo = SessionManager.getUser()
            if userInfo['id'] != userId:
                abort(406)

            parameters = request.json
            if not 'visionId' in parameters or \
               not 'srcIndex' in parameters or \
               not 'destIndex' in parameters:
                abort(406)
            visionId = parameters['visionId']
            srcIndex = parameters['srcIndex']
            destIndex = parameters['destIndex']

            Logger.debug("V:%s src: %s dest: %s" % (visionId, srcIndex, destIndex))

            user = User.getById(userInfo['id'])
            result = user.moveVision(visionId, srcIndex, destIndex)

            if True == result:
                data = { 'result' : "success" }
            else:
                data = { 'result' : "error" }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/user/<int:userId>/delete_vision', methods=['POST'])
def apiDeleteUserVision(userId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():

            userInfo = SessionManager.getUser()
            if userInfo['id'] != userId:
                abort(406)

            parameters = request.json
            if not 'visionId' in parameters:
                abort(406)
            visionId = parameters['visionId']
            
            user = User.getById(userInfo['id'])
            data = { 'result' : "error" }
            if user:
                result = user.deleteVision(visionId)
                if True == result:
                    data = { 'result'    : "success",
                            'removedId' : visionId }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/user/<int:userId>/repost_vision', methods=['POST'])
def apiRepostVision(userId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():

            userInfo = SessionManager.getUser()
            if userInfo['id'] != userId:
                abort(406)

            parameters = request.json
            if not 'visionId' in parameters:
                abort(406)
            visionId = parameters['visionId']

            user = User.getById(userInfo['id'])
            data = { 'result' : "error" }
            if user:
                vision = Vision.getById(visionId, user)
                if vision:
                    newVision = user.repostVision(vision)
                    if newVision:
                        data = { 'result'    : "success",
                                 'repostParentId' : visionId,
                                 'newVision'      : newVision.toDictionary() }
            return jsonify(data)
        abort(403)
    abort(405)



@app.route('/api/user/<int:userId>/like_vision', methods=['POST'])
def apiLikeVision(userId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():

            userInfo = SessionManager.getUser()
            if userInfo['id'] != userId:
                abort(406)

            parameters = request.json
            if not ('visionId' in parameters or
                    'like' in parameters):
                abort(406)
            visionId = parameters['visionId']
            like = parameters['like']

            user = User.getById(userInfo['id'])
            data = { 'result' : "error" }
            if user:
                vision = Vision.getById(visionId, user)
                if vision:
                    if like == True:
                        vision.like(user)
                    else:
                        vision.unlike(user)
                    data = { 'result'    : "success",
                             'like' : vision.likedBy(user),
                             'likeCount' : vision.likeCount() }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/user/<int:userId>/like_vision_comment', methods=['POST'])
def apiLikeVisionComment(userId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():

            userInfo = SessionManager.getUser()
            if userInfo['id'] != userId:
                abort(406)

            parameters = request.json
            if not ('visionCommentId' in parameters and
                    'like' in parameters):
                abort(406)
            visionCommentId = parameters['visionCommentId']
            like = parameters['like']

            user = User.getById(userInfo['id'])
            data = { 'result' : "error" }
            if user:
                comment = VisionComment.getById(visionCommentId)
                if comment:
                    vision = Vision.getById(comment.visionId(), user)
                    if vision:
                        if like == True:
                            comment.like(user)
                        else:
                            comment.unlike(user)
                        data = { 'result'    : "success",
                                 'like' : comment.likedBy(user),
                                 'likeCount' : comment.likeCount() }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/user/<int:userId>/follow_user', methods=['POST'])
def apiFollowUser(userId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():

            userInfo = SessionManager.getUser()
            if userInfo['id'] != userId:
                abort(406)

            parameters = request.json
            if not ('userId' in parameters or
                    'follow' in parameters):
                abort(406)
            userToFollowId = parameters['userId']
            follow = parameters['follow']

            if userToFollowId == userId:
                # can't follow or unfollow self
                abort(406)

            user = User.getById(userInfo['id'])
            userToFollow = User.getById(userToFollowId)
            data = { 'result' : "error" }
            if user and userToFollow:
                if follow:
                    user.followUser(userToFollow)
                else:
                    user.unfollowUser(userToFollow)

                userToFollowDict = userToFollow.toDictionary(
                                        options=[User.Options.FOLLOW_COUNTS,
                                                 User.Options.FOLLOWING],
                                        user=user)
                meDict = user.toDictionary(options=[User.Options.FOLLOW_COUNTS])
                data = { 'result'    : "success",
                         'user' : userToFollowDict,
                         'me'   : meDict
                       }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/user/<int:userId>/follows', methods=['POST'])
def apiUserFollows(userId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():
            parameters = request.json
            if not ('userId' in parameters):
                abort(406)
            assert userId == parameters['userId'], "Invalid user"

            myInfo = SessionManager.getUser()
            me = User.getById(myInfo['id'])
            user = User.getById(userId)

            data = { 'result' : "error" }
            if me and user:
                follows = user.getFollows()

                data = { 'result'    : "success",
                         'users' : follows.toDictionary(
                                    options=[FollowList.Options.FOLLOW_LIST,
                                             FollowList.Options.USER_FOLLOW],
                                    user=me)
                       }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/user/<int:userId>/followers', methods=['POST'])
def apiUserFollowers(userId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():
            parameters = request.json
            if not ('userId' in parameters):
                abort(406)
            assert userId == parameters['userId'], "Invalid user"

            myInfo = SessionManager.getUser()
            me = User.getById(myInfo['id'])
            user = User.getById(userId)

            data = { 'result' : "error" }
            if me and user:
                follows = user.getFollowers()

                data = { 'result'    : "success",
                         'users' : follows.toDictionary(
                                    options=[FollowList.Options.FOLLOWER_LIST,
                                             FollowList.Options.USER_FOLLOW],
                                    user=me)
                       }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/vision/<int:visionId>/likes', methods=['POST'])
def apiVisionLikes(visionId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():
            parameters = request.json
            if not ('visionId' in parameters):
                abort(406)
            assert visionId == parameters['visionId'], "Invalid vision id"

            userInfo = SessionManager.getUser()
            user = User.getById(userInfo['id'])

            data = { 'result' : "error" }
            if user:
                vision = Vision.getById(visionId, user)
                if vision:
                    userList = vision.getLikesUserList()

                    data = { 'result'    : "success",
                             'users' : userList.toDictionary(
                                        options=[UserList.Options.USER_FOLLOW],
                                        user=user)
                        }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/vision_comment/<int:visionCommentId>/likes', methods=['POST'])
def apiVisionCommentLikes(visionCommentId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():
            parameters = request.json
            if not ('visionCommentId' in parameters):
                abort(406)
            assert visionCommentId == parameters['visionCommentId'], \
                   "Invalid vision comment id"

            userInfo = SessionManager.getUser()
            user = User.getById(userInfo['id'])
            comment = VisionComment.getById(visionCommentId)
            data = { 'result' : "error" }
            if user and comment:
                vision = Vision.getById(comment.visionId(), user)

                if vision:
                    userList = comment.getLikesUserList()

                    data = { 'result'    : "success",
                            'users' : userList.toDictionary(
                                        options=[UserList.Options.USER_FOLLOW],
                                        user=user)
                        }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/user/<int:userId>/file_upload', methods=['POST'])
def apiFileUpload(userId):
    errorResult = { 'result' : 'error' }

    if request.method == 'POST':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            if userInfo['id'] != userId:
                return render_template('file_upload.html',
                                       jsonResult=errorResult)

            file = request.files['picture']
            user = User.getById(userInfo['id'])
            url = user.previewImage(file)

            if url:
                SessionManager.setPreviewUrl(url)
                successResult = ({'result' : 'success',
                                    'url'    : url})
                return render_template('file_upload.html',
                                        jsonResult=successResult)
    return render_template('file_upload.html', jsonResult=errorResult)

@app.route('/api/user/<int:userId>/add_vision', methods=['POST'])
def apiAddUserVision(userId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            if userInfo['id'] != userId:
                abort(406)

            parameters = request.json
            if not 'useImage' in parameters or \
               not 'text'     in parameters or \
               not 'privacy'  in parameters:
                abort(406)
            useImage = parameters['useImage']
            text = parameters['text'].strip()
            isPublic = parameters['privacy']

            Logger.debug("IsPublic: " + str(isPublic))

            # Make sure input OK to create a new vision
            if useImage == False:
            # TODO: should we allow text w/o image?
            #if useImage == False and len(text) == 0:
                abort(406)

            # Make sure image link OK
            url = ""
            if useImage == True:
                url = SessionManager.getPreviewUrl()

            # Create a new vision with the photo
            user = User.getById(userId)
            
            # Make sure we have a valid user
            if not user:
                data = {'result' : "error"}

            else:
                vision, errorMsg = user.addVision(url, text, True, isPublic)

                if vision:
                    objList = []
                    if None != vision:
                        objList = VisionList.createFromVision(vision)
                    if len(objList.visions()) == 1:
                        data = { 'result'    : "success",
                                 'newVision' : objList.toDictionary(
                                        options=[Vision.Options.PICTURE,
                                                 Vision.Options.USER,
                                                 Vision.Options.PARENT_USER,
                                                 Vision.Options.COMMENT_PICTURES,
                                                 Vision.Options.COMMENTS])[0] }

                else:
                    data = { 'result' : "error" }

            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/vision/<int:visionId>/add_comment', methods=['POST'])
def apiAddVisionComment(visionId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()

            parameters = request.json
            if not ('visionId' in parameters and \
                    'text' in parameters):
                abort(406)
            if visionId == parameters['visionId']:
                authorId = userInfo['id']
                text = parameters['text']
                
                user = User.getById(userInfo['id'])
                if user:
                    newComment = user.commentOnVision(visionId, text)
                    if newComment:
                        data = { 'result'    : "success",
                                 'newComment' : newComment.toDictionary(
                                     options=[VisionComment.Options.AUTHOR,
                                              VisionComment.Options.LIKES],
                                     user=user)
                            }
                    return jsonify(data)
            data = { 'result' : "error" }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/vision/add_picture_comment', methods=['POST'])
def apiAddVisionPictureComment():
    if request.method == 'POST':
        parameters = request.form
        if not ('text' in parameters and 
                'userId' in parameters and
                'visionId' in parameters):
            abort(406)
        if not 'picture' in request.files:
            abort(406)

        file = request.files['picture']
        userId = int(parameters['userId'])
        visionId = int(parameters['visionId'])
        user = User.getById(userId)
        url = user.previewImage(file)

        if user and url and userId > 0 and visionId > 0:
            # We now have url to use for comment
            text = parameters['text']

            newComment, error_msg = user.pictureCommentOnVision(visionId,
                                                                text, url)
            if newComment:
                data = { 'result'    : "success",
                            'newComment' : newComment.toDictionary(
                                options=[VisionComment.Options.AUTHOR,
                                         VisionComment.Options.PICTURE,
                                         VisionComment.Options.LIKES],
                                user=user)
                        }
                return jsonify(data)
        data = { 'result' : "error",
                    'error_msg' : error_msg }
        return jsonify(data)
    abort(405)

@app.route('/api/vision/<int:visionId>/edit', methods=['POST'])
def apiVisionEdit(visionId):
    if request.method == 'POST':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()

            parameters = request.json
            if not ('visionId' in parameters and
                    'text' in parameters and
                    'isPublic' in parameters):
                abort(406)
            if visionId != parameters['visionId']:
                abort(406)
            text = parameters['text']
            isPublic = parameters['isPublic']

            user = User.getById(userInfo['id'])
            vision = Vision.getById(visionId, user)
            if (vision == None) or vision.userId() != userInfo['id']:
                abort(406)

            (change, errorMsg) = vision.edit(text, isPublic);

            data = { 'result' : "error" }
            if change and errorMsg == "":
                data = { 'result'    : "success",
                         'text'      : text,
                         'isPublic'  : isPublic,
                         'errorMsg'  : "",
                       }
            elif errorMsg != "":
                data = { 'result' : "success", 
                         'errorMsg':  errorMsg
                       }
            return jsonify(data)
        abort(403)
    abort(405)

@app.route('/api/vision/<int:visionId>/comments', methods=['POST'])
def apiVisionComments(visionId):
    if request.method == 'POST':
        userId = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            userId = userInfo['id']

        parameters = request.json
        if (not 'visionId' in parameters) or \
           parameters['visionId'] != visionId:
            abort(406)
       
        user = User.getById(userId)
        vision = Vision.getById(visionId, user)
        data = { 'result' : "error" }
        if vision:
            # Get reposts
            repostUsers = vision.repostUsers()
            repostObjs = []
            for repostUser in repostUsers:
                repostObjs.append(repostUser.toDictionary())

            # Get original user
            rootUserObj = None
            visionListObj = None
            rootVision = vision.rootVision(user)
            if rootVision:
                rootUser = User.getById(rootVision.userId())
                if rootUser:
                    rootUserObj = rootUser.toDictionary()
                    visions = rootUser.visionList(user)
                    if visions and visions.length() > 0:
                        visions.limitLength(6)
                        visionListObj = visions.toDictionary(
                                              options=[Vision.Options.PICTURE])
            # Get comments
            commentObjs = []
            comments = vision.comments(100)
            if comments:
                commentObjs = comments.toDictionary(
                                        options=[VisionComment.Options.AUTHOR,
                                                 VisionComment.Options.LIKES,
                                                 VisionComment.Options.PICTURE],
                                        user=user)

            # package them up
            data = {'result' : 'success',
                    Vision.Key.COMMENTS : commentObjs,
                    Vision.Key.REPOST_USERS  : repostObjs }
            if rootUserObj and visionListObj:
                data['rootUser'] = rootUserObj
                data['rootUserVisions'] = visionListObj
        return jsonify(data)
    abort(405)

'''
    Save
    Used for Bookmarklet
'''
@app.route('/vision/create/bookmarklet', methods=['GET'])
def bookmarkletCreate():

    #Make we only accept get
    if request.method != 'GET': abort(405)

    #Check login
    #TODO: Pass the referring url to the login function so we can return here!
    if not SessionManager.userLoggedIn():
        return redirect(url_for('login'))

    #Get Parameters
    '''
    callback = request.args.get('callback', '')
    mimetype = 'application/javascript'
    '''

    mediaUrl = request.args.get(Constant.BOOKMARKLET_MEDIA_URL_KEY)
    mediaDescription = request.args.get(Constant.BOOKMARKLET_MEDIA_DESCRIPTION_KEY)
    pageUrl = request.args.get(Constant.BOOKMARKLET_PAGE_URL_KEY)
    pageTitle = request.args.get(Constant.BOOKMARKLET_PAGE_TITLE_KEY)

    #Validate Parameter
    #if callback == '':
        #return "Please make a valid request!"

    #Validate Parameters
    if mediaUrl is None \
        or mediaDescription is None \
        or pageUrl is None \
        or pageTitle is None:
        return "Please submit the valid data"
        #content = callback + "('Please submit the valid data!')"
        #return current_app.response_class(content, mimetype=mimetype)

    userInfo = SessionManager.getUser()
    user = User.getById(userInfo['id'])
    checkText = ""
    if not user.visionDefaultIsPublic():
        checkText = "checked"

    return render_template('create.html', mediaUrl=mediaUrl,
                                          mediaDescription=mediaDescription,
                                          pageUrl=pageUrl,
                                          pageTitle=pageTitle,
                                          checkText=checkText)


@app.route('/vision/create/bookmarklet', methods=['POST'])
def create():

    '''
    Debugging Tip:
    if you see: 

        Bad Request
        The browser (or proxy) sent a request that this server could not understand.

    (a 400 error)

    Make sure all of the form fields are given correctly

    http://stackoverflow.com/questions/8552675/form-sending-error-flask
    '''

    mediaUrl = request.form[Constant.BOOKMARKLET_POST_MEDIA_URL]
    text = request.form[Constant.BOOKMARKLET_POST_TEXT]
    pageUrl = request.form[Constant.BOOKMARKLET_POST_PAGE_URL]
    pageTitle = request.form[Constant.BOOKMARKLET_POST_PAGE_TITLE]

    #Vision Privacy
    private = False
    if Constant.BOOKMARKLET_POST_IS_PRIVATE in request.form:
        private = True

    #Format for saving
    visionIsPublic = not private

    #Validate Parameters
    if mediaUrl is None \
        or text is None \
        or pageUrl is None \
        or pageTitle is None:
        return "Invalid Vision Parameters"

    Logger.debug("URL: " + mediaUrl)

    #Question: Do we really need to check the login again here?
    #Check Login
    if not SessionManager.userLoggedIn():
        return redirect(url_for('login'))

    #Get the user id
    userId = SessionManager.getUser()['id']

    #Add
    user = User.getById(userId)
    if user:
        # TODO: should we save pageUrl and pageTitle also?
        vision, message = user.addVision(mediaUrl, text, False, visionIsPublic)

        if vision:
            #Successful Create!
            return render_template('successCreatingVision.html',
                                   visionId=vision.id(), userId=userId)
    #Error
    return render_template('errorCreatingVision.html', message=message)

@app.route('/about/postmarklet', methods=['GET'])
def about_postmarklet():
    if request.method == 'GET':
        userInfo = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
        return render_template('postmarklet.html',
                               user=userInfo, config=app.config)
    abort(405)

@app.route('/terms', methods=['GET'])
def terms():
    if request.method == 'GET':
        userInfo = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
        return render_template('terms.html', user=userInfo, config=app.config)
    abort(405)

@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            user = User.getById(userInfo['id'])
            if user and user.isAdmin():
                users = User.getAllUsers()
                return render_template('admin_dashboard.html',
                                       user=userInfo, config=app.config,
                                       userCount=User.getCount(),
                                       visionCount=Vision.getCount(),
                                       commentCount=VisionComment.getCount(),
                                       visionLikeCount=VisionLike.getCount(),
                                       commentLikeCount=VisionCommentLike.getCount(),
                                       followCount=Follow.getCount(),
                                       users=reversed(users))
        abort(403)
    abort(405)

# Target URL for New Relic availability monitoring
@app.route('/new_relic/ping', methods=['GET'])
def new_relic_ping_target():
    return "pong..."

@app.route('/rq/test', methods=['GET'])
def rq_test():
    from WorkerJobs import Queue_print
    Queue_print("Hello world")
    return "testing..."

# Target URL for New Relic availability monitoring
@app.route('/test/<emailType>', methods=['GET'])
def test_email(emailType):
    if request.method == 'GET':
        userInfo = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            user = User.getById(userInfo['id'])
            if user and user.isAdmin():
                notification = Notifications()
                if emailType == "daily":
                    return notification.testDailyEmail()
                elif emailType == "welcome":
                    return notification.testWelcomeEmail(userInfo)
    return "Hello."

@app.route('/test/pictureComment', methods=['GET'])
def testPictureComment():
    if request.method == 'GET':
        userInfo = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
        return render_template('testPictureComment.html', user=userInfo, config=app.config)
    abort(405)

# $eof
