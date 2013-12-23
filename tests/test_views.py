# -*- coding: utf-8 -*-

from django.utils.translation import gettext as _
import pytest
from concurrency.views import conflict
from tests.util import with_all_models
#
#
# @pytest.mark.django_db
# @with_all_models
# def test_conflict(model_class, rf):
#     instance, __ = model_class.objects.get_or_create(username=text(10))
#     request = rf.get('/customer/details', target=instance)
#     response = conflict(request)
#     assert response.status_code == 409
#
