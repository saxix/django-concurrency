#!/usr/bin/env python
import imp
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
init = os.path.join(ROOT, 'src', 'concurrency', '__init__.py')
app = imp.load_source('concurrency', init)

reqs = 'install.py%d.pip' % sys.version_info[0]

rel = lambda fname: os.path.join(os.path.dirname(__file__),
                                 'src',
                                 'requirements', fname)


def fread(fname):
    return open(rel(fname)).read()

install_requires = fread('install.pip')
test_requires = fread('testing.pip')
dev_requires = fread('develop.pip')

base_url = 'https://github.com/saxix/django-concurrency/'


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
    setup_requires=['pytest-runner', ],
    install_requires=install_requires,
    tests_require='django\n' + test_requires,
    extras_require={'test': test_requires,
                    'dev': test_requires + dev_requires},
    # cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
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
