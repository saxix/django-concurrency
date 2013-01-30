import os

SITE_ID = 1
ROOT_URLCONF = 'demoproject.urls'
SECRET_KEY = ';klkj;okj;lkn;lklj;lkj;kjmlliuewhy2ioqwjdkh'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'concurrency')



from demoproject.settings_sqlite import *
db = os.environ.get('DBENGINE', None)
if db:
    mod = __import__('demoproject.settings_%s' % db, fromlist=['demoproject'])
    DATABASES = mod.DATABASES

