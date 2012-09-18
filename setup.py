#!/usr/bin/env python
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
import concurrency

NAME = 'django-concurrency'
RELEASE = concurrency.get_version()
base_url = 'https://github.com/saxix/django-concurrency/'
VERSIONMAP = {'final': (concurrency.VERSION, 'Development Status :: 5 - Production/Stable'),
              'rc': (concurrency.VERSION, 'Development Status :: 4 - Beta'),
              'beta': (concurrency.VERSION, 'Development Status :: 4 - Beta'),
              'alpha': ('master', 'Development Status :: 3 - Alpha')}

download_tag, development_status = VERSIONMAP[concurrency.VERSION[3]]

setup(
    name=NAME,
    version=RELEASE,
    url='https://github.com/saxix/django-concurrency',
    download_url='http://pypi.python.org/packages/source/d/django-concurrency/django-concurrency-%s.tar.gz' % RELEASE,
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    packages=[
        "concurrency",
        "concurrency.tests",
    ],
    description="Optimistic locking library for Django",
    license="MIT License",
    keywords="django",
    classifiers=[
        development_status,
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms=['any'],
)
