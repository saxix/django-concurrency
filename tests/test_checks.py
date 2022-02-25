import logging

import pytest
from demo.models import TriggerConcurrentModel

logger = logging.getLogger(__name__)


@pytest.fixture
def obj():
    return TriggerConcurrentModel.objects.create()


@pytest.mark.django_db
def test_check(obj, monkeypatch):
    from django.core.checks import Warning
    monkeypatch.setattr(obj._concurrencymeta.field, '_trigger_name', 'test')

    assert isinstance(obj._concurrencymeta.field.check()[0], Warning)
