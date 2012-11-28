from flask.ext.sqlalchemy import SQLAlchemy

#Add the api.py (parent) folder
import os
import sys
dir = os.path.dirname(__file__)

relativeDataApiPath = "../../../"
OBJECT_FILES_PATH = os.path.join(dir, relativeDataApiPath)
sys.path.append(OBJECT_FILES_PATH)

from awesome import app

DB = SQLAlchemy(app)

