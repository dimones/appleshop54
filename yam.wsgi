import sys,os,platform

sys.stdout = sys.stderr
if 'api' not in platform.uname().node:
    sys.path.insert(0, os.getenv("MYNSTU_LOCATION"))
else:
    sys.path.insert(0, '/var/www/appleshop54')

import logging
logger = logging.getLogger('')

logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stderr)

handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)-8s %(message)s')

handler.setFormatter(formatter)

logger.addHandler(handler)
from appleshop54 import app as application
