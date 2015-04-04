import os
from tempfile import mktemp
import django

DEBUG = True
STATIC_URL = '/static/'

SITE_ID = 1
ROOT_URLCONF = 'demo.urls'
SECRET_KEY = 'abc'
STATIC_ROOT = mktemp('static')
MEDIA_ROOT = mktemp('media')

INSTALLED_APPS = ['django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'django.contrib.messages',
                  'django.contrib.staticfiles',
                  'django.contrib.admin',
                  # 'django.contrib.admin.apps.SimpleAdminConfig'
                  'concurrency',
                  'demo']

SOUTH_MIGRATION_MODULES = {
    'demo': 'demo.south_migrations',
}

MIGRATION_MODULES = {
    'demo': 'demo.migrations',
    'auth': 'demo.auth_migrations',
}

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
if django.VERSION[1] >= 7:
    MIDDLEWARE_CLASSES += ['django.contrib.auth.middleware.SessionAuthenticationMiddleware', ]

TEMPLATE_DIRS = ['demo/templates']

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
            'class': 'logging.NullHandler'
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

db = os.environ.get('DBENGINE', 'pg')
if db == 'pg':
    DATABASES = {
        'default': {
            # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'ENGINE': 'concurrency.db.backends.postgresql_psycopg2',
            'NAME': 'concurrency',
            'HOST': '127.0.0.1',
            'PORT': '',
            'USER': 'postgres',
            'PASSWORD': ''}}
elif db == 'mysql':
    DATABASES = {
        'default': {
            # 'ENGINE': 'django.db.backends.mysql',
            'ENGINE': 'concurrency.db.backends.mysql',
            'NAME': 'concurrency',
            'HOST': '127.0.0.1',
            'PORT': '',
            'USER': 'root',
            'PASSWORD': '',
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
            'TEST_CHARSET': 'utf8',
            'TEST_COLLATION': 'utf8_general_ci'}}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'concurrency.db.backends.sqlite3',
            'NAME': 'concurrency.sqlite',
            'HOST': '',
            'PORT': ''}}
