from flask import render_template
from flask import abort, redirect, url_for, flash, jsonify
from flask import request, session
from flask import Response

from . import APP

from api.data.api import *

@APP.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        if 'user' in session:
            userName = session['user']['userName']
            return render_template('index.html', userName=userName)
        else:
            return render_template('index.html', userName='')
    abort(405)

@APP.route('/profile', methods=['GET'])
def user_profile():
    if request.method == 'GET':
        if 'user' in session:
            userName = session['user']['userName']
            return render_template('index.html', userName=userName)
        else:
            return render_template('index.html', userName='')
    abort(405)

@APP.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user' in session:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    elif request.method == 'POST':
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

@APP.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@APP.route('/api/get_shared_visions', methods=['GET'])
def apiGetSharedVisions():
    textVision = { 'visionId' : 1,
                   'category' : 'stuff',
                   'text'     : 'What?',
                   'photoUrl' : '',
                   'isPrivate' : False,
                   'isGloballyShared' : False,
                   'isFbShared' : False
                 }
    imageVision = { 'visionId' : 1,
                   'category' : 'stuff',
                   'text'     : 'Le Tigre',
                   'photoUrl' : 'http://mynethome.net/blog/wp-content/uploads/2009/05/derek-zoolander.jpg',
                   'isPrivate' : False,
                   'isGloballyShared' : False,
                   'isFbShared' : False
                 }

    data = { 'visionList' : [] }

    data['visionList'].append(textVision)
    data['visionList'].append(imageVision)
    data['visionList'].append(textVision)
    data['visionList'].append(textVision)
    data['visionList'].append(textVision)
    data['visionList'].append(imageVision)
    data['visionList'].append(textVision)
    data['visionList'].append(imageVision)
    data['visionList'].append(textVision)
    data['visionList'].append(textVision)
    data['visionList'].append(imageVision)
    data['visionList'].append(textVision)
    data['visionList'].append(textVision)
    data['visionList'].append(textVision)
    data['visionList'].append(textVision)
    data['visionList'].append(imageVision)
    data['visionList'].append(textVision)
    data['visionList'].append(textVision)
    data['visionList'].append(textVision)

    return jsonify(data)

@APP.route('/api/get_user_visions', methods=['GET'])
def apiGetUserVisions():
    textVision = { 'visionId' : 1,
                   'category' : 'stuff',
                   'text'     : 'What?',
                   'photoUrl' : '',
                   'isPrivate' : False,
                   'isGloballyShared' : False,
                   'isFbShared' : False
                 }
    imageVision = { 'visionId' : 1,
                   'category' : 'stuff',
                   'text'     : 'Le Tigre',
                   'photoUrl' : 'http://mynethome.net/blog/wp-content/uploads/2009/05/derek-zoolander.jpg',
                   'isPrivate' : False,
                   'isGloballyShared' : False,
                   'isFbShared' : False
                 }

    data = { 'visionList' : [] }

    data['visionList'].append(textVision)
    data['visionList'].append(imageVision)
    data['visionList'].append(textVision)
    data['visionList'].append(textVision)
    
    return jsonify(data)

