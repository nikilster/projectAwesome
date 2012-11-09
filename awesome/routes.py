from flask import render_template
from flask import abort, redirect, url_for, flash, jsonify
from flask import request, session
from flask import Response

from . import APP

@APP.route('/', methods=['GET'])
def index():
    return render_template('index.html')

