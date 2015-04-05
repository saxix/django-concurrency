# -*- coding: utf-8 -*-
import logging
from django.core.management import call_command
from django.db import connections
from django.utils.translation import gettext as _
from mock import Mock
import pytest
import six

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_command_create(monkeypatch):
    # dummy test to avoid stupid mistakes
    #
    mock_create = Mock()

    monkeypatch.setattr(connections['default'].creation, '_create_trigger', mock_create)
    call_command('triggers', 'create', stdout=Mock())
    assert mock_create.call_count == 1


@pytest.mark.django_db
def test_command_drop(monkeypatch):
    # dummy test to avoid stupid mistakes
    #
    mock_drop = Mock()

    monkeypatch.setattr(connections['default'], 'drop_trigger', mock_drop)
    call_command('triggers', 'drop', stdout=Mock())

    assert mock_drop.call_count == 2


@pytest.mark.django_db
def test_command_list():
    out = six.StringIO()
    call_command('triggers', 'list', stdout=out)
    out.seek(0)
    output = out.read()
    assert output.find('concurrency_demo_triggerconcurrentmodel_i')
    assert output.find('concurrency_demo_triggerconcurrentmodel_u')
