"""Production settings file for flowcellproject"""

import os

from .base import *

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

# Enabling WhiteNoise middleware for serving static files -------------------

MIDDLEWARE_CLASSES += [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# Interpret X-Forwarded-Proto Header ----------------------------------------

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# ... and enforce HTTPS connection
SECURE_SSL_REDIRECT = True

# Static files (CSS, JavaScript, Images) ------------------------------------

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = ()

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
