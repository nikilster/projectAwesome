import os
from awesome import APP

port = int(os.environ.get('PORT', 5000))
APP.run(host='0.0.0.0', port=port, debug=APP.config['DEBUG'])

