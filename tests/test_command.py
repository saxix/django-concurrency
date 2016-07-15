# -*- coding: utf-8 -*-
import logging

import six
from django.core.management import call_command

import pytest
from mock import Mock

import concurrency.management.commands.triggers as command

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_command_create(monkeypatch):
    out = six.StringIO()
    mock_create = Mock()
    mock_create.return_value = {'default': [['model', 'field', 'trigger']]}

    monkeypatch.setattr(command, 'create_triggers', mock_create)
    call_command('triggers', 'create', stdout=out)

    out.seek(0)
    output = out.read()
    assert output.find('Created trigger  for field') > 0
    assert mock_create.call_count == 1


@pytest.mark.django_db
def test_command_list():
    out = six.StringIO()
    call_command('triggers', 'list', stdout=out)
    out.seek(0)
    output = out.read()
    assert output.find('concurrency_demo_triggerconcurrentmodel_i')
    assert output.find('concurrency_demo_triggerconcurrentmodel_u')


@pytest.mark.django_db
def test_command_drop(monkeypatch):
    out = six.StringIO()
    mock_drop = Mock()
    mock_drop.return_value = {'default': [['model', 'field', 'trigger']]}

    monkeypatch.setattr(command, 'drop_triggers', mock_drop)
    call_command('triggers', 'drop', stdout=out)

    out.seek(0)
    output = out.read()
    assert output.find('Dropped   trigger') > 0
    assert mock_drop.call_count == 1
