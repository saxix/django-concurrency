import pytest
from django.apps import apps
from django.db import connections
from concurrency.triggers import get_triggers, drop_triggers, create_triggers, _TRIGGERS, TriggerRegistry
from demo.models import TriggerConcurrentModel


@pytest.mark.django_db
def test_get_triggers():
    triggers = get_triggers()
    assert "default" in triggers
    assert isinstance(triggers["default"], list)


@pytest.mark.django_db
def test_drop_create_triggers():
    drop_triggers(*list(connections))

    for app_label, model_name in _TRIGGERS:
        model = apps.get_model(app_label, model_name)
        model._concurrencymeta.triggers = []

    created = create_triggers(list(connections))
    assert "default" in created
    assert len(created["default"]) > 0

    created_again = create_triggers(list(connections))
    assert "default" not in created_again


def test_trigger_registry():
    registry = TriggerRegistry()

    class MockModel:
        class _meta:  # noqa
            app_label = "test_app"

    class MockField:
        model = MockModel

    registry.append(MockField)
    assert MockField in registry

    for item in registry:
        assert item == ["test_app", "MockModel"]


@pytest.mark.django_db
def test_get_trigger_name():
    from concurrency.triggers import get_trigger_name  # noqa

    field = TriggerConcurrentModel._concurrencymeta.field
    name = get_trigger_name(field)
    assert name.startswith("concurrency_")
