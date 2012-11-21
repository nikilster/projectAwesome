import os, sys
from flask import Flask

# Ensure tmp folder exists for picture uploads
LOCAL_IMAGE_DIR = 'awesome/static/tmp_image'
if not os.path.exists(LOCAL_IMAGE_DIR):
  os.makedirs(LOCAL_IMAGE_DIR)

#Application
app = Flask(__name__)
app.secret_key = '\xaf\xd6\xd9.\x9c\xc8\x16CL\x14#\xe5\x07T\xf8\xe9\xad\xf0\x0e\xcbO"6\x91'

from routes import *

#Debug
app.config['DEBUG'] = True

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    app.run()
