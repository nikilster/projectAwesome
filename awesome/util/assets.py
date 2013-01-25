#
# Defines asset bundles, and provides genAssets() for generating minified
# versions of them.
#

from awesome import app
from flask.ext.assets import Environment, Bundle

assets = Environment(app)

#
# JS Bundles
#
JS_home = Bundle(
    'opt/jquery-1.7.2.js',
    'opt/bootstrap/js/bootstrap.min.js',
    'opt/jquery-ui-1.8.20/js/jquery-ui-1.8.15.custom.min.js',
    'opt/jquery.masonry.js',
    'opt/jquery.autosize.js',
    'opt/jquery.placeholder.js',
    'opt/underscore.js',
    'opt/backbone.js',
    'opt/date.js',
    'opt/backbone.analytics-master/backbone.analytics.js',

    'js/Util.js',
    'js/Global.js',

    # Order seems to matter between models and collections
    'js/models/User.js',
    'js/collections/UserList.js',
    'js/models/Picture.js',
    'js/models/Like.js',
    'js/models/VisionComment.js',
    'js/collections/VisionCommentList.js',
    'js/models/Vision.js',
    'js/collections/VisionList.js',
    'js/models/Activity.js',
    'js/collections/ActivityList.js',
    'js/models/Page.js',

    'js/views/UserInformation.js',
    'js/views/Like.js',
    'js/views/VisionComment.js',
    'js/views/VisionDetailsComment.js',
    'js/views/VisionDetails.js',
    'js/views/Vision.js',
    'js/views/UserList.js',
    'js/views/Activity.js',
    'js/views/Page.js',

    'js/routers/Router.js',

    'js/home.js',
    filters='jsmin',
    output='gen/js/home.min.js'
)
assets.register('js_home', JS_home)

JS_base = Bundle(
    'opt/jquery-1.7.2.js',
    'opt/bootstrap/js/bootstrap.min.js',
    'opt/jquery.placeholder.js',
    filters='jsmin',
    output='gen/js/base.min.js'
)
assets.register('js_base', JS_base)

#
# CSS Bundles
#
CSS_home = Bundle(
    'opt/bootstrap/css/bootstrap.css',
    'css/index.css',
    filters='cssmin',
    output='gen/css/home.min.css'
)
assets.register('css_home', CSS_home)

CSS_base = Bundle(
    'opt/bootstrap/css/bootstrap.css',
    'css/register.css',
    filters='cssmin',
    output='gen/css/base.min.css'
)
assets.register('css_base', CSS_base)

def _gen_asset(name):
  print "Generating asset: " + name
  assets[name].urls()

#
# Generate assets: call this to generate minified bundles
#

def genAssets():
    _gen_asset('js_home')
    _gen_asset('js_base')
    _gen_asset('css_home')
    _gen_asset('css_base')

# $eof
