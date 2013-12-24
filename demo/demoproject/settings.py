from tests.settings import *
ROOT_URLCONF = 'demoproject.urls'
INSTALLED_APPS = ['django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'django.contrib.messages',
                  'django.contrib.staticfiles',
                  'django.contrib.admin',
                  'concurrency',
                  'demoproject.demoapp',
                  'tests']
# AUTHENTICATION_BACKENDS = ('demoproject.backends.AnyUserBackend',)
