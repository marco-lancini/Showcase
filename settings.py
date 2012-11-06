#=========================================================================
# IMPORT
#=========================================================================
from djangoappengine.settings_base import *
from settings_private import *
import social_auth
import os

#=========================================================================
# SETTINGS
#=========================================================================
#TODO - deploy
DEBUG          = False      # true = show errors, false = 404
DEVELOPMENT    = False       # true = localhost, false = gae
TEMPLATE_DEBUG = DEBUG

PROJECT_NAME = 'Showcase'
ADMINS       = ( ('Marco Lancini', 'marco@marcolancini.it'), )
MANAGERS     = ADMINS
ROOT_PATH    = os.path.abspath( os.path.dirname(__file__) )


#=========================================================================
# ACTIVATION EMAILS
#=========================================================================
ACCOUNT_ACTIVATION_DAYS = 7
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST    = 'smtp.gmail.com'
EMAIL_PORT    = 587
EMAIL_USE_TLS = True



# Activate django-dbindexer for the default database
DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
AUTOLOAD_SITECONF = 'indexes'

#SECRET_KEY = '^n(j932h$czj=cav9j#s^)7z@z73&amp;yc$w=puu!9lthcccc!2%7'

INSTALLED_APPS = (
#    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'djangotoolbox',
    'autoload',
    'dbindexer',

    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
)

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come first
    'autoload.middleware.AutoloadMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)

# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
# TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

ADMIN_MEDIA_PREFIX = '/media/admin/'
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)

ROOT_URLCONF = 'urls'
