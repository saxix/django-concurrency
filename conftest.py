import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

import os
import sys
from django.conf import settings

def pytest_collection_modifyitems(items):
    pass


def pytest_configure(config):
    here = os.path.dirname(__file__)
    sys.path.insert(0, here)


    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'


def runtests(args=None):
    import pytest

    if not args:
        args = []

    if not any(a for a in args[1:] if not a.startswith('-')):
        args.append('concurrency')

    sys.exit(pytest.main(args))


if __name__ == '__main__':
    runtests(sys.argv)
