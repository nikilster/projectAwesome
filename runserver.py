import os
from awesome.Constant import Constant
from awesome import app

# Ensure tmp folder exists for picture uploads
if not os.path.exists(Constant.LOCAL_IMAGE_DIR):
  os.makedirs(Constant.LOCAL_IMAGE_DIR)

#Run
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

