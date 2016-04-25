"""Local settings file for cbioportal_users"""

import os

from .base import *

# Locally, it is OK to use a static, insecure key
SECRET_KEY = 'I am not very secure :('

# Enable debugging locally
DEBUG = True

# Allow all hosts
ALLOWED_HOSTS = []

# Locally, fix to using sqlite3
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'cbioportal': dj_database_url.parse(os.environ['DATABASE_URL_CBIOPORTAL']),
}

# Static files (CSS, JavaScript, Images) ------------------------------------

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'
