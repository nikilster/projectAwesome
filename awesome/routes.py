from flask import render_template
from flask import abort, redirect, url_for, flash, jsonify
from flask import request, session
from flask import Response

from . import APP

@APP.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@APP.route('/api/get_test_vision_list', methods=['GET'])
def apiGetTestVisionList():
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

    return jsonify(data)
