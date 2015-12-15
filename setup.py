#!/usr/bin/env python
import os
import sys
from distutils import log
from distutils.command.clean import clean as CleanCommand
from distutils.dir_util import remove_tree

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(ROOT, 'src'))

app = __import__('concurrency')
base_url = 'https://github.com/saxix/django-concurrency/'
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


class Clean(CleanCommand):
    user_options = CleanCommand.user_options + [
        ('build-coverage=', 'c',
         "build directory for coverage output (default: 'build.build-coverage')"),
    ]

    def initialize_options(self):
        self.build_coverage = None
        self.build_help = None
        CleanCommand.initialize_options(self)

    def run(self):
        if self.all:
            for directory in (os.path.join(self.build_base, 'coverage'),
                              os.path.join(self.build_base, 'help')):
                if os.path.exists(directory):
                    remove_tree(directory, dry_run=self.dry_run)
                else:
                    log.warn("'%s' does not exist -- can't clean it",
                             directory)
        if self.build_coverage:
            remove_tree(self.build_coverage, dry_run=self.dry_run)
        if self.build_help:
            remove_tree(self.build_help, dry_run=self.dry_run)
        CleanCommand.run(self)

install_requires = ["django"]
test_requires = ["django-webtest>=1.7.5",
                 "mock>=1.0.1",
                 "pytest-cache>=1.0",
                 "pytest-cov>=1.6",
                 "pytest-django>=2.8",
                 "pytest-echo>=1.3",
                 "pytest-pythonpath",
                 "pytest>=2.8",
                 "tox>=2.3",
                 "WebTest>=2.0.11"]

dev_requires = ["autopep8",
                "coverage",
                "django_extensions",
                "flake8",
                "ipython",
                "pdbpp",
                "psycopg2",
                "sphinx"]

setup(
    name=app.NAME,
    version=app.get_version(),
    url='https://github.com/saxix/django-concurrency',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    description='Optimistic lock implementation for Django. Prevents users from doing concurrent editing.',
    long_description=open('README.rst').read(),
    license='MIT License',
    keywords='django',
    install_requires=install_requires,
    tests_require=test_requires,
    extras_require={'test': test_requires,
                    'dev': test_requires + dev_requires},
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
