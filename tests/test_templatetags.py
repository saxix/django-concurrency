# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import logging

import pytest

from concurrency.templatetags.concurrency import identity, version, is_version
from demo.models import SimpleConcurrentModel

logger = logging.getLogger(__name__)


@pytest.fixture
def obj():
    return SimpleConcurrentModel.objects.create()


@pytest.mark.django_db
def test_identity(obj):
    assert identity(obj).split(',') == [str(obj.pk), str(obj.version)]


@pytest.mark.django_db
def test_version(obj):
    assert version(obj) == obj.version


@pytest.mark.django_db
def test_is_version(obj):
    assert is_version(obj._concurrencymeta.field)
