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
PROJECT_NAME = 'Showcase'
ADMINS       = ( ('Marco Lancini', 'marco@marcolancini.it'), )
MANAGERS     = ADMINS

DEBUG          = False
TEMPLATE_DEBUG = DEBUG

ROOT_PATH = os.path.abspath( os.path.dirname(__file__) )
BASE_URL  = 'http://showcase-st1.appspot.com/'


#=========================================================================
# DB AND CACHE
#=========================================================================
DATABASES['native']  = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
AUTOLOAD_SITECONF    = 'indexes'


#=========================================================================
# INSTALLED APPS
#=========================================================================
INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'djangotoolbox',
    'autoload',
    'dbindexer',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # # SUPPORT APPS
    # 'respite',
    # 'registration',
    # 'social_auth',
    # # CUSTOM APPS
    # 'app_auth',
    # 'app_collaborations',
    # 'app_hints',
    # 'app_projects',
    # 'app_socialnetworks',
    # 'app_users',
    #
    'djangoappengine',
)






# INSTALLED_APPS = (
# #    'django.contrib.admin',
#     'django.contrib.contenttypes',
#     'django.contrib.auth',
#     'django.contrib.sessions',
#     'djangotoolbox',
#     'autoload',
#     'dbindexer',

#     # djangoappengine should come last, so it can override a few manage.py commands
#     'djangoappengine',
# )

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





#=========================================================================
# ACTIVATION EMAILS
#=========================================================================
ACCOUNT_ACTIVATION_DAYS = 7
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST    = 'smtp.gmail.com'
EMAIL_PORT    = 587
EMAIL_USE_TLS = True
