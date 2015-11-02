# -*- coding: utf-8 -*-
import logging
from django.core.management import call_command
from mock import Mock
import pytest
import six

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_command_create(monkeypatch):
    import concurrency.triggers
    mock_create = Mock()

    monkeypatch.setattr(concurrency.triggers, 'create_triggers', mock_create)
    call_command('triggers', 'create', stdout=Mock())
    assert mock_create.call_count == 1


# @pytest.mark.django_db
# def test_command_drop(monkeypatch):
#     # dummy test to avoid stupid mistakes
#     #
#     mock_drop = Mock()
#
#     monkeypatch.setattr(TriggerFactory, 'drop', mock_drop)
#     call_command('triggers', 'drop', stdout=Mock())
#
#     assert mock_drop.call_count == 1


@pytest.mark.django_db
def test_command_list():
    out = six.StringIO()
    call_command('triggers', 'list', stdout=out)
    out.seek(0)
    output = out.read()
    assert output.find('concurrency_demo_triggerconcurrentmodel_i')
    assert output.find('concurrency_demo_triggerconcurrentmodel_u')
