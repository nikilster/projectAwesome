from flask import render_template
from flask import abort, redirect, url_for, flash, jsonify
from flask import request, session
from flask import Response

from . import APP

from util.Logger import Logger

from api.Api import Api
from api.FlashMessages import *

@APP.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        if 'user' in session:
            userName = session['user']['userName']
            return render_template('index.html', userName=userName)
        else:
            return render_template('index.html', userName='')
    abort(405)

@APP.route('/view_board', methods=['GET'])
def view_board():
    return redirect(url_for('index'))

@APP.route('/profile', methods=['GET'])
def user_profile():
    if request.method == 'GET':
        if 'user' in session:
            userName = session['user']['userName']
            return render_template('index.html', userName=userName)
        else:
            return render_template('index.html', userName='')
    abort(405)

@APP.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@APP.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user' in session:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        session['user'] = { 'userName' : 'Derek' }
        return redirect (url_for('index'))
    abort(405)

@APP.route('/logout', methods=['GET'])
def logout():
    if request.method == 'GET':
        if 'user' in session:
            session.pop('user', None)
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

@APP.route('/register_user', methods=['POST'])
def register_user():
    if request.method == 'POST':
        firstName = request.form['firstName'].strip()
        lastName = request.form['lastName'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        
        '''
        selectedVisions = []
        if 'selectedVisions' in session:
            selectedVisionsJson = session['selectedVisions']
        '''

        (newUserId, errorMsg) = Api.addUser(firstName, lastName,
                                            email, password)

        Logger.debug("NEW USER ID: " + str(newUserId))
        if None != newUserId:
            newUser = Api.getUserById(newUserId)
            assert newUser, "New user should exist"

            '''
                Logger.debug("Existing selected visions: " +
                            str(session['selectedVisions']))
            '''

            session['user'] = { 'userName' : newUser.firstName }

            return redirect(url_for('user_profile'))
        else:
            assert errorMsg != "", "Error message should exist"
            flash(errorMsg, RegisterError.TAG)
            return redirect(url_for('register'))
    abort(405)

@APP.route('/api/get_main_page_visions', methods=['GET'])
def apiGetMainPageVisions():
    visions = Api.getMainPageVisions()

    data = { 'visionList' : [] }

    for vision in visions:
        data['visionList'].append(vision.toDictionary())

    return jsonify(data)

@APP.route('/api/get_user_visions', methods=['GET'])
def apiGetUserVisions():
    visions = Api.getVisionsForUser(1)

    data = { 'visionList' : [] }

    for vision in visions:
        data['visionList'].append(vision.toDictionary())

    return jsonify(data)

# $eof
