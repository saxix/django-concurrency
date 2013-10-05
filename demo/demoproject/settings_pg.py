DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'concurrency',
        'HOST': '127.0.0.1',
        'PORT': '',
        'USER': 'postgres',
        'PASSWORD': '',
        'OPTIONS': {
            'autocommit': True,  # same value for all versions of django (is the default in 1.6)
        }}}
