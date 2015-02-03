"""
Django settings for acacia project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lyh)8hhwcz*a7i-o9ndk(7j0(%e25o3ji^7e+anqq4e)f^7#y('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['.acaciadata.com', 'localhost']

# Application definition
INSTALLED_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'bootstrap3',
    'registration',
    'south',
    'acacia',
    'acacia.data',
    'acacia.data.knmi',
    'spaarwater',
    'vic',
)

MIDDLEWARE_CLASSES = (
    'sentry.client.middleware.SentryResponseErrorIdMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'acacia.data.middleware.XsSharing',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)

ROOT_URLCONF = 'acacia.urls'

WSGI_APPLICATION = 'acacia.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
#     'default': {
#         'ENGINE': 'django.contrib.gis.db.backends.spatialite',
#         'NAME': os.path.join(BASE_DIR, 'acaciadata.db'),                      # Or path to database file if using sqlite3.
#     },
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'acaciadata',                      # Or path to database file if using sqlite3.
        'USER': 'acacia',                      # Not used with sqlite3.
        'PASSWORD': 'Beaumont1',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'nl-nl'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
UPLOAD_DATAFILES = 'datafiles' 
UPLOAD_THUMBNAILS = 'thumbnails' 
UPLOAD_IMAGES = 'images' 

# Grapelli admin
GRAPPELLI_ADMIN_TITLE='Beheer van Acacia Online Datastore'

# registration stuff
ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_REDIRECT_URL = '/data/'

# Celery stuff
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND='redis://localhost:6379/0'
INSTALLED_APPS += ('kombu.transport.django','djcelery',)    
              
import djcelery
djcelery.setup_loader()
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

# sentry
RAVEN_CONFIG = {
    'dsn': 'http://68706cd5c9e94922ac0fb6ec6a5e4bc0:4116c9ed3dda453297548b36c2519d20@localhost:9000/3',
#    'dsn': 'http://68706cd5c9e94922ac0fb6ec6a5e4bc0@localhost:9000/3',
}

# RAVEN_CONFIG = {
#     'dsn': 'http://abcd823b4d544afba65f7bd710db155c:acb589fdc9e5427c81b2f0b08278496b@localhost:9000/2'
# }

# Add raven to the list of installed apps
INSTALLED_APPS = INSTALLED_APPS + (
    # ...
    'raven.contrib.django.raven_compat',
)

# Previous celery stuff
#BROKER_URL = 'django://'
#CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'
#INSTALLED_APPS += ('kombu.transport.django','djcelery',)                  

LOGGING_ROOT = os.path.join(BASE_DIR, 'logs')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'acacia.log'),
            'when': 'D',
            'interval': 1, # every day a new file
            'backupCount': 0,
            'formatter': 'default'
        },
        'django': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'django.log'),
            'when': 'D',
            'interval': 1, # every day a new file
            'backupCount': 0,
        },
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
    },
    'formatters': {
        'default': {
            'format': '%(levelname)s %(asctime)s %(name)s: %(message)s'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['django'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'acacia.data': {
            'handlers': ['file','sentry'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
