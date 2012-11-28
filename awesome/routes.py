from flask import render_template
from flask import abort, redirect, url_for, flash, jsonify
from flask import request, session
from flask import Response
from flask import current_app

from . import app
from Constant import Constant
import json

import shutil

import os
from werkzeug import secure_filename
import calendar, datetime, hashlib

from util.Logger import Logger

from api.Api import Api
from api.FlashMessages import *

from util.SessionManager import SessionManager

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        Logger.debug("SESSION CLASS: " + session.__class__.__name__)
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('index.html', user=userInfo)
        else:
            return render_template('index.html', user=None)
    abort(405)

@app.route('/view_board', methods=['GET'])
def view_board():
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET'])
def user_profile():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('index.html', user=userInfo)
        else:
            return render_template('index.html', user=None)
    abort(405)

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

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
            SessionManager.addUser(user)
            return redirect(url_for('user_profile'))
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

            SessionManager.addUser(newUser)

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

            return redirect(url_for('user_profile'))
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
            data['visionList'] = Api.getUserVisionList(userInfo['id'])

        return jsonify(data)
    abort(405)

@app.route('/api/get_user_visions', methods=['GET'])
def apiGetUserVisions():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            data = { 'visionList' : Api.getUserVisionList(userInfo['id']) }
            return jsonify(data)
        abort(403)
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

IMAGE_TYPES = dict({
    'png' : 'image/png',
    'jpg' : 'image/jpeg',
    'jpeg' : 'image/jpeg',
    'gif' : 'image/gif',
    'bmp' : 'image/x-ms-bmp',   # this one is unofficial
})

def image_ext(filename):
    parts = filename.rsplit('.',1)
    if len(parts) < 2:
        return None
    return parts[1].lower()

def image_filename_valid(filename):
    ext = image_ext(filename)
    if ext and ext in IMAGE_TYPES.keys():
        return True
    return False 

def userTempImagePath(userId, filename):
    path = Constant.LOCAL_IMAGE_DIR + '/TmpImage-' + str(userId) + "." + image_ext(filename)
    url = '/static/tmp_image/TmpImage-' + str(userId) + "." + image_ext(filename)
    return (path, url)
def userFinalImagePath(userId, filename):
    t = str(calendar.timegm(datetime.datetime.utcnow().timetuple()))
    md5 = hashlib.md5()
    md5.update(t)
    digest = md5.hexdigest()
    uniqueString = str(userId) + "_" + str(digest)

    path = Constant.LOCAL_IMAGE_DIR + '/' + uniqueString + "." + image_ext(filename)
    url = '/static/tmp_image/' + uniqueString + "." + image_ext(filename)

    return (path, url)

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

            if file and image_filename_valid(file.filename):
                filename = secure_filename(file.filename)
                path, url= userTempImagePath(userId, filename)
                file.save(path);
                file.close()
                SessionManager.setPreloadedImage(path)
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
                # Rename image, remove tmp file, and get photo pointer
                tmpPath = SessionManager.getPreloadedImage()
           
                # Get final url for image and copy tmp file to final url
                path, url = userFinalImagePath(userId, tmpPath)
                cwd = os.getcwd()
                #os.rename(os.path.join(cwd, tmpPath),
                #          os.path.join(cwd, path))
                shutil.copy2(os.path.join(cwd, tmpPath),
                             os.path.join(cwd, path))

            # Create a new vision with the photo
            visionId, errorMsg = Api.saveVision(userId, url, text, "", "")
            vision = Api.getVision(visionId)

            if None != vision:
                data = { 'result'    : "success",
                         'newVision' : vision.toDictionary() }
            else:
                data = { 'result' : "error" }
            return jsonify(data)
        abort(403)
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
    visionId, message = Api.saveVision(userId, mediaUrl, text, pageUrl, pageTitle)

    #Successful Create!
    if(visionId != Constant.INVALID_OBJECT_ID):
        return render_template('successCreatingVision.html', visionId=visionId)

    #Error
    return render_template('errorCreatingVision.html', message=message)

# $eof
