#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys
import concurrency

NAME = 'django-concurrency'
RELEASE = concurrency.get_version()
base_url = 'https://github.com/saxix/django-concurrency/'
VERSIONMAP = {'final': (concurrency.VERSION, 'Development Status :: 5 - Production/Stable'),
              'rc': (concurrency.VERSION, 'Development Status :: 4 - Beta'),
              'beta': (concurrency.VERSION, 'Development Status :: 4 - Beta'),
              'alpha': ('master', 'Development Status :: 3 - Alpha')}

download_tag, development_status = VERSIONMAP[concurrency.VERSION[3]]
install_requires = []
dev_requires = [
    'psycopg2>=2.5.0,<2.6.0',
    "ipdb",
    "django_extensions",
    "tox>=1.6.1",
]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name=NAME,
    version=RELEASE,
    url='https://github.com/saxix/django-concurrency',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    description="Optimistic lock implementation for Django. Prevents users from doing concurrent editing.",
    long_description=open('README.rst').read(),
    license="MIT License",
    keywords="django",
    install_requires=install_requires,
    cmdclass={'test': PyTest},
    classifiers=[
        development_status,
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django :: 1.4',
        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms=['any'],
)
