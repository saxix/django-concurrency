import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

import os
import sys


def pytest_collection_modifyitems(items):
    pass

# @pytest.fixture(scope="session")
# def superuser():
#     from django.contrib.auth.models import User
#     return User.objects.create_superuser('superuser', '', '123')
#
#
# @pytest.fixture(scope="module")
# def concurrentmodel():
#     from tests.models import SimpleConcurrentModel
#     return SimpleConcurrentModel.objects.get_or_create(username='user')[0]
#
#
# @pytest.fixture(scope='function')
# def app(request):
#     import django_webtest
#     wtm = django_webtest.WebTestMixin()
#     wtm._patch_settings()
#     request.addfinalizer(wtm._unpatch_settings)
#     return django_webtest.DjangoTestApp()


def pytest_configure(config):
    here = os.path.dirname(__file__)
    sys.path.insert(0, here)
    from django.conf import settings

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
