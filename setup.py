#!/usr/bin/env python
from setuptools import setup
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
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    packages=["concurrency",
              "concurrency.tests",
              "concurrency.templatetags"
    ],
    include_package_data=True,
    description="Optimistic locking library for Django",
    long_description=open('README.rst').read(),
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
