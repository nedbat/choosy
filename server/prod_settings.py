# Production settings.
from settings import *

# Hmm, this is what sucks about the --settings=prod_settings.py way of doing
# things: can't affect something in settings.py directly.
INSTALLED_APPS = [a for a in INSTALLED_APPS if a not in ['django_nose']]

DEBUG = False

STATIC_ROOT = '/home/nedbat/webapps/choosy_static/'
STATIC_URL = 'http://choosepython/static/'

EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'choosy'
EMAIL_HOST_PASSWORD = 'choosy_mailbox'
DEFAULT_FROM_EMAIL = 'choosy@choosepython.com'
SERVER_EMAIL = 'choosy@choosepython.com'
