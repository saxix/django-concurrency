import os
import sys
from django.conf import settings


def pytest_configure(config):
    here = os.path.dirname(__file__)
    sys.path.insert(0, os.path.join(here, 'demo'))

    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'demoproject.settings'
