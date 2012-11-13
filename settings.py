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
ADMINS       = ( ('Marco Lancini', 'marco@marcolancini.it'), 
                 ('Showcase', 'showcase.st1@gmail.com'),
                )
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

DBINDEXER_BACKENDS = (
    'dbindexer.backends.BaseResolver',
    'dbindexer.backends.FKNullFix',
    'dbindexer.backends.InMemoryJOINResolver',
)

# DEVELOPMENT
# # Running in development, so use a local MySQL database.
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'USER': 'stuser',
#         'PASSWORD': 'stpwd',
#         'HOST': 'localhost',
#         'NAME': 'ST1',
#     }
# }
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#     }
# }
# BASE_URL = 'http://127.0.0.1:8000'


#=========================================================================
# INSTALLED APPS
#=========================================================================
INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
    'djangotoolbox',
    'autoload',
    'dbindexer',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # SUPPORT APPS
    'respite',
    'registration',
    'social_auth',
    # CUSTOM APPS
    'app_auth',
    'app_collaborations',
    'app_hints',
    'app_projects',
    'app_socialnetworks',
    'app_users',
    # APP ENGINE
    'djangoappengine',
)


#=========================================================================
# HELPER LOADER
#=========================================================================
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.static',
    'django.core.context_processors.csrf',
    'django.contrib.messages.context_processors.messages',
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    #'social_auth.context_processors.social_auth_by_type_backends',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

MIDDLEWARE_CLASSES = (
    'autoload.middleware.AutoloadMiddleware',
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    #'app_auth.pipeline.SocialAuthExceptionMiddleware',
    'respite.middleware.HttpPutMiddleware',
    'respite.middleware.HttpPatchMiddleware',
    'respite.middleware.JsonMiddleware',
    'respite.middleware.HttpMethodOverrideMiddleware',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)


#=========================================================================
# AUTH
#=========================================================================
AUTH_PROFILE_MODULE = 'app_users.UserProfile'

LOGIN_URL          = '/login/'
LOGOUT_URL         = '/logout/'
LOGIN_ERROR_URL    = '/login/error/'
LOGIN_REDIRECT_URL = '/'

SOCIAL_AUTH_CREATE_USERS          = True
SOCIAL_AUTH_FORCE_RANDOM_USERNAME = False
SOCIAL_AUTH_DEFAULT_USERNAME      = 'socialauth_user'
SOCIAL_AUTH_COMPLETE_URL_NAME     = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME    = 'socialauth_associate_complete'
SOCIAL_AUTH_ERROR_KEY             = 'socialauth_error'
SOCIAL_AUTH_DEFAULT_USERNAME      = 'R2-D2'

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'app_auth.pipeline.redirect_to_ask_username',
    'app_auth.pipeline.username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'app_auth.pipeline.update_name',
    'app_auth.pipeline.redirect_to_ask_email',
    'app_auth.pipeline.email',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
    'social_auth.backends.contrib.tumblr.TumblrBackend',
    'social_auth.backends.contrib.flickr.FlickrBackend',
    #
    #'social_auth.backends.contrib.foursquare.FoursquareBackend',
    #'social_auth.backends.contrib.github.GithubBackend',
    #'social_auth.backends.contrib.dropbox.DropboxBackend',
    #'social_auth.backends.contrib.instagram.InstagramBackend',
    #
    #'social_auth.backends.OpenIDBackend',
    # 'social_auth.backends.google.GoogleOAuthBackend',
    # 'social_auth.backends.google.GoogleOAuth2Backend',
    #'social_auth.backends.yahoo.YahooBackend',
    #'social_auth.backends.browserid.BrowserIDBackend',
    #'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    #'social_auth.backends.contrib.orkut.OrkutBackend',
    #'social_auth.backends.contrib.vkontakte.VKontakteBackend',
    #'social_auth.backends.contrib.skyrock.SkyrockBackend',
    #'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
    #'social_auth.backends.contrib.bitbucket.BitbucketBackend',
    #'social_auth.backends.contrib.live.LiveBackend',
)


#=========================================================================
# LOCATIONS
#=========================================================================
ROOT_URLCONF  = 'urls'

# Absolute filesystem path to the directory that will hold templates
TEMPLATE_DIRS = os.path.join(ROOT_PATH, 'templates')

# Absolute filesystem path to the directory that will hold user-uploaded files
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself: store your static files in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files ("http://media.lawrence.com/static/")
STATIC_URL = os.path.join(ROOT_PATH, '/static/')

# Additional locations of static files
STATICFILES_DIRS = ( 'static/', )

# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'


#=========================================================================
# ACTIVATION EMAILS
#=========================================================================
ACCOUNT_ACTIVATION_DAYS = 7
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST    = 'smtp.gmail.com'
EMAIL_PORT    = 587
EMAIL_USE_TLS = True


#=========================================================================
# OTHER SETTINGS
#=========================================================================
TIME_ZONE     = 'Europe/Rome'
LANGUAGE_CODE = 'en-us'
SITE_ID       = 1
USE_I18N      = True
USE_L10N      = True
USE_TZ        = True
