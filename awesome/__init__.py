import os, sys
from flask import Flask

#Application
app = Flask(__name__)
app.secret_key = '\xaf\xd6\xd9.\x9c\xc8\x16CL\x14#\xe5\x07T\xf8\xe9\xad\xf0\x0e\xcbO"6\x91'

from util.Logger import Logger

from routes import *

# This should be the default configuration we want in production
class DEFAULT_CONFIG:
    DEBUG = True
    LOCAL_DB = False

app.config.from_object(DEFAULT_CONFIG)
if os.getenv('PROJECT_AWESOME_FLASK_SETTINGS'):
    app.config.from_envvar('PROJECT_AWESOME_FLASK_SETTINGS')
Logger.info("DEBUG=" + str(app.config['DEBUG']) +
            "  LOCAL_DB=" + str(app.config['LOCAL_DB']))
if app.config['LOCAL_DB'] == False:
    Logger.info(" ********   DO NOT MESS WITH PRODUCTION DB   ******** ")

#
# Configuration for MySQL
#
if app.config['LOCAL_DB']:
    DB_USER = 'projectAwesome'
    DB_PASSWORD = 'awesome'
    DB_HOST = 'localhost'
    DB_NAME = 'projectAwesome'
else:
    DB_USER = 'projectAwesome'
    DB_PASSWORD = 'aw3!s0m3'
    DB_HOST = 'maindb.cylmlzjscg1s.us-east-1.rds.amazonaws.com:3306'
    DB_NAME = 'projectAwesome'
DB_URI = 'mysql://%s:%s@%s/%s' % (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI

#
# S3 configuration variables
#
if app.config['LOCAL_DB']:
    S3_BUCKET_NAME = 'test-project-awesome-img'
else:
    S3_BUCKET_NAME = 'project-awesome-img'
S3_HTTPS_HEADER = 'https://s3.amazonaws.com/'


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    app.run()
