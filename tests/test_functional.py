from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django_webtest import WebTestMixin
import django_webtest
import pytest
from tests.models import SimpleConcurrentModel


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    print 111.1


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    print 111.2


@pytest.fixture(scope="module")
def superuser():
    return User.objects.get_or_create(username='sax', is_superuser=True)[0]

@pytest.fixture(scope="module")
def concurrentmodel():
    return SimpleConcurrentModel.objects.get_or_create(username='sax')[0]

@pytest.fixture(scope='function')
def app(request):
    wtm = django_webtest.WebTestMixin()
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return django_webtest.DjangoTestApp()

#
# @pytest.mark.django_db
# @pytest.mark.functional
# def test_concurrent_edit(superuser, concurrentmodel, app):
#     res = app.get(reverse('concurrent-edit', args=[concurrentmodel.pk,]),
#                   user=superuser.username)
#     res.showbrowser()
