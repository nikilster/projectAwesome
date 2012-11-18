import os, sys
from flask import Flask

#Application
app = Flask(__name__)
app.secret_key = '\xaf\xd6\xd9.\x9c\xc8\x16CL\x14#\xe5\x07T\xf8\xe9\xad\xf0\x0e\xcbO"6\x91'

from routes import *

#Debug
app.config['DEBUG'] = True

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    app.run()
