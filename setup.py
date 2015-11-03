#!/usr/bin/env python
import os
import sys
import subprocess
import datetime
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
try:
    from concurrency import VERSION
except ImportError:
    sys.path.append('src')
    from concurrency import VERSION

NAME = 'django-concurrency'


def get_version(version):
    """Derives a PEP386-compliant version number from VERSION."""
    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:parts])

    sub = ''
    if version[3] == 'alpha' and version[4] == 0:
        git_changeset = get_git_changeset()
        if git_changeset:
            sub = '.a%s' % git_changeset

    elif version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]]
        if version[4] > 0:
            sub += str(version[4])

    return main + sub


def get_git_changeset():
    """Returns a numeric identifier of the latest git changeset.

The result is the UTC timestamp of the changeset in YYYYMMDDHHMMSS format.
This value isn't guaranteed to be unique, but collisions are very unlikely,
so it's sufficient for generating the development version numbers.
"""
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_log = subprocess.Popen('git log --pretty=format:%ct --quiet -1 HEAD',
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               shell=True, cwd=repo_dir,
                               universal_newlines=True)
    timestamp = git_log.communicate()[0]
    try:
        timestamp = datetime.datetime.utcfromtimestamp(int(timestamp))
    except ValueError:
        return None
    return timestamp.strftime('%Y%m%d%H%M%S')


RELEASE = get_version(VERSION)
base_url = 'https://github.com/saxix/django-concurrency/'
VERSIONMAP = {'final': (VERSION, 'Development Status :: 5 - Production/Stable'),
              'rc': (VERSION, 'Development Status :: 4 - Beta'),
              'beta': (VERSION, 'Development Status :: 4 - Beta'),
              'alpha': ('master', 'Development Status :: 3 - Alpha')}

download_tag, development_status = VERSIONMAP[VERSION[3]]
install_requires = []


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        import sys
        sys.path.insert(0, os.path.join(ROOT, 'tests', 'demoapp'))
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name=NAME,
    version=RELEASE,
    url='https://github.com/saxix/django-concurrency',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    # packages=find_packages(),

    package_dir={'': 'src'},
    packages=find_packages('src'),

    include_package_data=True,
    description='Optimistic lock implementation for Django. Prevents users from doing concurrent editing.',
    long_description=open('README.rst').read(),
    license='MIT License',
    keywords='django',
    install_requires=install_requires,
    cmdclass={'test': PyTest},
    classifiers=[
        development_status,
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms=['any'],
)
