from .base import *

DEBUG = True

INTERNAL_IPS = ['127.0.0.1']

# Debug toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# Email backend for dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable SSL redirect
SECURE_SSL_REDIRECT = False
