from flask import render_template
from flask import abort, redirect, url_for, flash, jsonify
from flask import request, session
from flask import Response

from . import APP

import json

from util.Logger import Logger

from api.Api import Api
from api.FlashMessages import *

from util.SessionManager import SessionManager


@APP.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        Logger.debug("SESSION CLASS: " + session.__class__.__name__)
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('index.html', userName=userInfo['firstName'])
        else:
            return render_template('index.html', userName='')
    abort(405)

@APP.route('/view_board', methods=['GET'])
def view_board():
    return redirect(url_for('index'))

@APP.route('/profile', methods=['GET'])
def user_profile():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()
            return render_template('index.html', userName=userInfo['firstName'])
        else:
            return render_template('index.html', userName='')
    abort(405)

@APP.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@APP.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        Logger.debug("Email: " + str(email))

        (user, errorMsg) = Api.loginUser(email, password)

        if user:
            Logger.debug("Name: " + user.firstName)
            SessionManager.addUser(user)
            return redirect(url_for('user_profile'))
        else:
            assert errorMsg != None, "Error msg should exist"
            flash(errorMsg, LoginError.TAG)
            return redirect (url_for('login'))
    abort(405)

@APP.route('/logout', methods=['GET'])
def logout():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            SessionManager.removeUser();
        return redirect(url_for('index'))
    abort(405)

@APP.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        # Keep selected visions in session
        if 'selectedVisions' in request.form:
            session['selectedVisions'] = str(request.form['selectedVisions'])
        return render_template('register.html')
    abort(405)

@APP.route('/register_user', methods=['POST'])
def register_user():
    if request.method == 'POST':
        firstName = request.form['firstName'].strip()
        lastName = request.form['lastName'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        
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

@APP.route('/api/get_main_page_visions', methods=['GET'])
def apiGetMainPageVisions():
    if request.method == 'GET':
        visions = Api.getMainPageVisions()

        data = { 'visionList' : [] }
        for vision in visions:
            data['visionList'].append(vision.toDictionary())

        return jsonify(data)
    abort(405)

@APP.route('/api/get_user_visions', methods=['GET'])
def apiGetUserVisions():
    if request.method == 'GET':
        if SessionManager.userLoggedIn():
            userInfo = SessionManager.getUser()

            visions = Api.getVisionsForUser(userInfo['id'])

            data = { 'visionList' : [] }
            for vision in visions:
                data['visionList'].append(vision.toDictionary())

            return jsonify(data)
        abort(403)
    abort(405)

@APP.route('/api/user/<int:userId>/move_vision', methods=['POST'])
def apiUserMoveVision(userId):
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

# $eof
