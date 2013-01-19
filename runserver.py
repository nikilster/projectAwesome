import os
from awesome.Constant import Constant
from awesome import app

# Ensure tmp folder exists for picture uploads
if not os.path.exists(Constant.LOCAL_IMAGE_DIR):
  os.makedirs(Constant.LOCAL_IMAGE_DIR)

#Run
app.run(port=6705, debug=app.config['DEBUG'])

