import os
from awesome.Constant import Constant
from awesome import app

# Ensure tmp folder exists for picture uploads
if not os.path.exists(Constant.LOCAL_IMAGE_DIR):
  os.makedirs(Constant.LOCAL_IMAGE_DIR)

if os.getenv('PORT'):
    port = os.getenv('PORT')
else:
    port = 5000

#Run
app.run(port=port, debug=app.config['DEBUG'])

