from flask import render_template
from flask import abort, redirect, url_for, flash, jsonify
from flask import request, session
from flask import Response

from . import APP

from flash_messages import *

from util.Logger import Logger
from util.PasswordEncrypt import PasswordEncrypt
from util.Verifier import Verifier

from api.data.DataApi import DataApi

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
        firstName = request.form['firstName'].strip()
        lastName = request.form['lastName'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        if not Verifier.nameValid(firstName):
            flash(RegisterError.FIRST_NAME_REQUIRED, RegisterError.TAG)
        elif not Verifier.nameValid(lastName):
            flash(RegisterError.LAST_NAME_REQUIRED, RegisterError.TAG)
        elif len(email) <= 0:
            flash(RegisterError.EMAIL_REQUIRED, RegisterError.TAG)
        elif not Verifier.emailValid(email):
            flash(RegisterError.EMAIL_INVALID, RegisterError.TAG)
        # TODO: NEED TO CHECK EMAIL EXISTS
        elif len(password) <= 0:
            flash(RegisterError.PASSWORD_REQUIRED, RegisterError.TAG)
        elif not Verifier.passwordValid(password):
            flash(RegisterError.PASSWORD_INVALID, RegisterError.TAG)
        else:
            passwordHash = PasswordEncrypt.genHash(password)

            verified = PasswordEncrypt.verifyPassword(password, passwordHash)

            # Just need to add new user here and login

            Logger.debug("Name: %s %s, Email: %s, Pass: %s [%s] -- %s" % \
                         (firstName, lastName, email,
                          password, passwordHash, str(verified)))

        return render_template('register.html')
    abort(405)

@APP.route('/api/get_main_page_visions', methods=['GET'])
def apiGetMainPageVisions():
    visions = DataApi.getMainPageVisions()

    data = { 'visionList' : [] }

    for vision in visions:
        data['visionList'].append(vision.__dict__)

    return jsonify(data)

@APP.route('/api/get_user_visions', methods=['GET'])
def apiGetUserVisions():
    visions = DataApi.getVisionsForUser(1)

    Logger.debug("Hello")

    data = { 'visionList' : [] }

    for vision in visions:
        data['visionList'].append(vision.__dict__)

    return jsonify(data)

# $eof
