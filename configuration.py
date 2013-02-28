""" WhoYou: Simple accounts database for web applications.

Configuration settings.
"""

import logging
import os.path
import sys
import socket
import urllib


DEBUG = False

HOST = dict(title='SciLifeLab tools',
            href='http://localhost/')

DATA_DIR = '/var/local/whoyou'

SALT = 'default123'

MIN_PASSWORD_LENGTH = 6


#----------------------------------------------------------------------
# Do not change anything below this.
#----------------------------------------------------------------------
# The 'site_XXX' module may redefine any of the above global variables.
HOSTNAME = socket.gethostname().split('.')[0]
MODULENAME = "whoyou.site_%s" % HOSTNAME
try:
    __import__(MODULENAME)
except ImportError:
    raise NotImplementedError("host %s" % HOSTNAME)
else:
    module = sys.modules[MODULENAME]
    for key in dir(module):
        if key.startswith('_'): continue
        globals()[key] = getattr(module, key)
#----------------------------------------------------------------------


if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

SOURCE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(SOURCE_DIR, 'static')

README_FILE = os.path.join(SOURCE_DIR, 'README.md')
MASTER_DB_FILE = os.path.join(DATA_DIR, 'master.sql3')
