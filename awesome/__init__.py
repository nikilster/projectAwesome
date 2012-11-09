import os, sys

from flask import Flask

APP = Flask(__name__)

APP.config['DEBUG'] = True

from routes import *

APP.secret_key = '\xaf\xd6\xd9.\x9c\xc8\x16CL\x14#\xe5\x07T\xf8\xe9\xad\xf0\x0e\xcbO"6\x91'

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    APP.run(host='0.0.0.0', port=port, debug=APP.config['DEBUG'])
