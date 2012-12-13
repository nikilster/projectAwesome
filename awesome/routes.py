from flask import render_template
from flask import abort, redirect, url_for, flash, jsonify
from flask import request, session
from flask import Response
from flask import current_app

from . import app
from Constant import Constant
import json

import os
import calendar, datetime

from util.Logger import Logger
from api.S3Util import ImageFilePreview

from api.Api import Api
from api.FlashMessages import *


from util.SessionManager import SessionManager

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('index.html', user=userInfo)
        else:
            return render_template('index.html', user=None)
    abort(405)

@app.route('/view_board', methods=['GET'])
def view_board():
    return redirect(url_for('index'))

@app.route('/user/<int:userId>', methods=['GET'])
def user_profile(userId):
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('index.html', user=userInfo)
        else:
            return render_template('index.html', user=None)
    abort(405)

@app.route('/about', methods=['GET'])
def about():
    if request.method == 'GET':
        userInfo = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
        return render_template('about.html', user=userInfo)
    abort(405)

@app.route('/settings', methods=['GET'])
def settings():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('settings.html', user=userInfo)
        else:
            return render_template('index.html', user=None)
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

            result = Api.changeUserInfo(userInfo['id'],
                                        firstName, lastName, email, desc)
            Logger.debug("RESULT: " + str(result))

            # make sure to update session
            user = Api.getUserById(userInfo['id'])
            assert user, "New user should exist"
            SessionManager.setUser(user)
            userInfo = SessionManager.getUser()

            return render_template('settings.html', user=userInfo)
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

            result = Api.changeUserDescription(userInfo['id'], description)

            if True == result:
                data = { 'result' : "success",
                         'description' : description }
            else:
                data = { 'result' : "error" }
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

            url = Api.changeProfilePicture(userInfo['id'], file)

            user = Api.getUserById(userInfo['id'])
            assert user, "New user should exist"
            SessionManager.setUser(user)
            userInfo = SessionManager.getUser()

            return redirect(url_for('settings'))
        abort(406)
    abort(405)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        (user, errorMsg) = Api.loginUser(email, password)

        if user:
            SessionManager.setUser(user)
            return redirect(url_for('user_profile', userId=user.id))
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
        return render_template('register.html')
    elif request.method == 'POST':
        # Keep selected visions in session
        if 'selectedVisions' in request.form:
            session['selectedVisions'] = str(request.form['selectedVisions'])
        return render_template('register.html')
    abort(405)

@app.route('/register_user', methods=['POST'])
def register_user():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        
        (newUserId, errorMsg) = Api.registerUser(firstName, lastName,
                                                 email, password)

        Logger.debug("NEW USER ID: " + str(newUserId))
        if None != newUserId:
            newUser = Api.getUserById(newUserId)
            assert newUser, "New user should exist"

            SessionManager.setUser(newUser)

            # Add selected visions if list input valid
            selectedVisions = []
            if 'selectedVisions' in session:
                data = None
                try:
                    data = json.loads(session['selectedVisions'])
                except:
                    pass
                if data != None and isinstance(data, list):
                    ok = True
                    for item in data:
                        if not isinstance(item, int):
                            ok = False
                            break
                    if True == ok:
                        selectedVisions = data

                if len(selectedVisions) > 0:
                    Logger.debug("Existing selected visions: " +
                                 str(session['selectedVisions']))

                    Api.repostVisionList(newUser.id, selectedVisions)
                    session.pop('selectedVisions', None)

            return redirect(url_for('user_profile', userId=newUser.id))
        else:
            assert errorMsg != "", "Error message should exist"
            flash(errorMsg, RegisterError.TAG)
            return redirect(url_for('register'))
    abort(405)

@app.route('/api/get_main_page_visions', methods=['GET'])
def apiGetMainPageVisions():
    if request.method == 'GET':
        data = { 'otherVisions' : Api.getMainPageVisionList(),
                 'visionList'   : [] }

        # TODO: be smarter about when to load user vision list later
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            data['visionList'] = Api.getUserVisionList(userInfo['id'],
                                                       userInfo['id'])

        return jsonify(data)
    abort(405)

@app.route('/api/user/<int:userId>/visions', methods=['GET'])
def apiGetUserVisions(userId):
    if request.method == 'GET':
        data = {}
        myUserId = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            myUserId = userInfo['id']
            data['visionList'] = Api.getUserVisionList(userInfo['id'],
                                                       userInfo['id'])
        else:
            data['visionList'] = []

        data['otherVisions'] = Api.getUserVisionList(myUserId, userId)
        user = Api.getUserById(userId)
        data['user'] = user.toDictionary();

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

            result = Api.moveUserVision(userInfo['id'], visionId,
                                        srcIndex, destIndex)

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

            result = Api.deleteUserVision(userInfo['id'], visionId)

            if True == result:
                data = { 'result'    : "success",
                         'removedId' : visionId }
            else:
                data = { 'result' : "error" }
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

            newVision = Api.repostVision(userInfo['id'], visionId)

            if None != newVision:
                data = { 'result'    : "success",
                         'repostParentId' : visionId,
                         'newVision'      : newVision.toDictionary() }
            else:
                data = { 'result' : "error" }
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
            url = Api.previewImage(userInfo['id'], file)

            if None != url:
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
               not 'text'     in parameters:
                abort(406)
            useImage = parameters['useImage']
            text = parameters['text'].strip()

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
            visionId, errorMsg = Api.saveVision(userId, url, text, "", "",
                                                True)
            vision = Api.getVision(visionId)

            objList = []
            if None != vision:
                objList = Api._visionListToObjectList([vision])
            if len(objList) == 1:
                data = { 'result'    : "success",
                         'newVision' : objList[0] }
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
            
                newComment = Api.addVisionComment(visionId, userInfo['id'],
                                                  text)
                # Manually putting in name and picture id
                # TODO: doing this in Api for vision list too!
                #       ..implement better later!
                obj = newComment.toDictionary()
                author = Api.getUserById(authorId)
                obj['name'] = author.fullName
                obj['picture'] = author.picture
                if None != newComment:
                    data = { 'result'    : "success",
                             'newComment' : obj }
                    return jsonify(data)

            data = { 'result' : "error" }
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
        
        comments = Api.getVisionComments(visionId, userId)
        if None != comments:
            data = { 'result'    : "success",
                     'comments' : comments }
        else:
            data = { 'result' : "error" }
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
        return render_template('login.html')

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


    return render_template('create.html', mediaUrl=mediaUrl, mediaDescription=mediaDescription,\
        pageUrl=pageUrl, pageTitle=pageTitle)


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

    #Validate Parameters
    if mediaUrl is None \
        or text is None \
        or pageUrl is None \
        or pageTitle is None:
        return "Invalid Vision Parameters"


    #Question: Do we really need to check the login again here?
    #Check Login
    if not SessionManager.userLoggedIn():
        return render_template('login.html')

    #Get the user id
    userId = SessionManager.getUser()['id']

    #Add
    visionId, message = Api.saveVision(userId, mediaUrl, text,
                                       pageUrl, pageTitle, False)

    #Successful Create!
    if(visionId != Constant.INVALID_OBJECT_ID):
        return render_template('successCreatingVision.html', visionId=visionId)

    #Error
    return render_template('errorCreatingVision.html', message=message)

@app.route('/terms', methods=['GET'])
def terms():
    if request.method == 'GET':
        userInfo = None
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
        return render_template('terms.html', user=userInfo)
    abort(405)

# Target URL for New Relic availability monitoring
@app.route('/new_relic/ping', methods=['GET'])
def new_relic_ping_target():
    return "pong..."
    
# $eof
