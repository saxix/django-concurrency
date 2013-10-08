import os

DEBUG = True
STATIC_URL = '/static/'
AUTHENTICATION_BACKENDS = ('demoproject.backends.AnyUserBackend',)

SITE_ID = 1
ROOT_URLCONF = 'demoproject.urls'
SECRET_KEY = ';klkj;okj;lkn;lklj;lkj;kjmlliuewhy2ioqwjdkh'

INSTALLED_APPS = ['django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'django.contrib.messages',
                  'django.contrib.staticfiles',
                  'django.contrib.admin',
                  'concurrency',
                  'concurrency.tests',
                  'demoproject.demoapp']
#
#MIDDLEWARE_CLASSES = ('django.middleware.common.CommonMiddleware',
#                      'concurrency.middleware.ConcurrencyMiddleware',
#                       'django.contrib.sessions.middleware.SessionMiddleware',
#                       'django.middleware.csrf.CsrfViewMiddleware',
#                       'django.contrib.auth.middleware.AuthenticationMiddleware',
#                       'django.contrib.messages.middleware.MessageMiddleware',)
#
#CONCURRENCY_HANDLER409 = 'demoproject.demoapp.views.conflict'
#CONCURRENCY_POLICY = 2

try:
    import import_export  # NOQA

    INSTALLED_APPS.append('import_export')
except ImportError:
    pass

TEMPLATE_DIRS = ['demoproject/templates']
from demoproject.settings_sqlite import *  # NOQA

db = os.environ.get('DBENGINE', None)
if db:
    mod = __import__('demoproject.settings_%s' % db, fromlist=['demoproject'])
    DATABASES = mod.DATABASES

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'full': {
            'format': '%(levelname)-8s: %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'verbose': {
            'format': '%(levelname)-8s: %(asctime)s %(name)-25s %(message)s'
        },
        'simple': {
            'format': '%(levelname)-8s %(asctime)s %(name)-25s %(funcName)s %(message)s'
        },
        'debug': {
            'format': '%(levelno)s:%(levelname)-8s %(name)s %(funcName)s:%(lineno)s:: %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'debug'
        }
    },
    'loggers': {
        'concurrency': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'DEBUG'
        }
    }
}
