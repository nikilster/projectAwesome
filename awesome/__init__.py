import os, sys
from flask import Flask

from boto.s3.connection import S3Connection

#Application
app = Flask(__name__)
app.secret_key = '\xaf\xd6\xd9.\x9c\xc8\x16CL\x14#\xe5\x07T\xf8\xe9\xad\xf0\x0e\xcbO"6\x91'

from util.Logger import Logger

# This should be the default configuration we want in production
class DEFAULT_CONFIG:
    DEBUG = True
    LOCAL_DB = False

# Get Config
app.config.from_object(DEFAULT_CONFIG)
if os.getenv('PROJECT_AWESOME_FLASK_SETTINGS'):
    app.config.from_envvar('PROJECT_AWESOME_FLASK_SETTINGS')

# Print current status of the config variables
Logger.info("DEBUG=" + str(app.config['DEBUG']) +
            "  LOCAL_DB=" + str(app.config['LOCAL_DB']))

#If we are using the production database
if app.config['LOCAL_DB'] == False:
  Logger.info(" ********   Using the Product DB - No not edit or wipe!   ******** ")

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
# TODO: For security, move access key and secret into environment variables!
#

os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAISAVPWDBZLJNNVNA'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
if not ('AWS_ACCESS_KEY_ID' in os.environ and
        'AWS_SECRET_ACCESS_KEY' in os.environ):
    sys.exit("Need AWS keys in environment")

if app.config['LOCAL_DB']:
    S3_BUCKET_NAME = 'test-project-awesome-img'
else:
    S3_BUCKET_NAME = 'project-awesome-img'
S3_HTTPS_HEADER = 'https://s3.amazonaws.com/'

S3_CONN = S3Connection()
UPLOAD_SIZE_LIMIT = 5 * 1024 * 1024

# Set flask max upload size limit
# - If file is larger, flask will raise RequestEntityTooLarge exception
app.config['MAX_CONTENT_LENGTH'] = UPLOAD_SIZE_LIMIT

from routes import *

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    app.run()
