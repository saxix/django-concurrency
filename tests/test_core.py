# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest
from demo.models import SimpleConcurrentModel

from concurrency.core import _select_lock
from concurrency.exceptions import RecordModifiedError
from concurrency.utils import refetch


@pytest.mark.django_db
def test_select_lock(settings):
    s1 = SimpleConcurrentModel.objects.create()
    s2 = refetch(s1)
    assert s1.version == s2.version
    s2.save()
    with pytest.raises(RecordModifiedError):
        _select_lock(s1)

    settings.CONCURRENCY_ENABLED = False
    _select_lock(s1)
