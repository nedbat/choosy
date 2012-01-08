from settings import *

INSTALLED_APPS = [a for a in INSTALLED_APPS if a not in ['django_nose']]

