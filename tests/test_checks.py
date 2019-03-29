# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging

import django

import pytest
from demo.models import TriggerConcurrentModel

logger = logging.getLogger(__name__)


@pytest.fixture
def obj():
    return TriggerConcurrentModel.objects.create()


@pytest.mark.skipif(django.VERSION[:2] < (1, 7),
                    reason="Skip if django< 1.7")
@pytest.mark.django_db
def test_check(obj, monkeypatch):
    from django.core.checks import Warning
    monkeypatch.setattr(obj._concurrencymeta.field, '_trigger_name', 'test')

    assert isinstance(obj._concurrencymeta.field.check()[0], Warning)
