import pytest
from demo.util import with_std_models
from django.db.models import Model
from django.db.models.query import QuerySet

from concurrency.config import conf
from concurrency.fields import _accepts_argument

pytest.mark.django_db(transaction=False)


def _django_core_supports_returning_fields() -> bool:
    # We intentionally inspect Django's core Model implementation rather than
    # our wrapped model method, because wrapping always adds a compatibility
    # argument even when the underlying Django runtime is pre-6.0.
    return _accepts_argument(Model._do_update, "returning_fields")


def _expected_updated_shape():
    # Django 6+ update internals expect list-based return shapes from _do_update
    # when "returning_fields" is part of the call contract.
    return [()] if _django_core_supports_returning_fields() else True


def _expected_not_updated_shape():
    # Django <6.0 uses bool return semantics for the same "updated/not updated"
    # signal.
    return [] if _django_core_supports_returning_fields() else False


@with_std_models
@pytest.mark.django_db(transaction=False)
def test_do_update_accepts_returning_fields(model_class):
    instance = model_class.objects.create(username="abc")

    updated = instance._do_update(
        model_class._base_manager.using(instance._state.db),
        instance._state.db,
        instance.pk,
        [],
        None,
        False,
        returning_fields=[],
    )

    assert updated


@pytest.mark.django_db(transaction=False)
def test_wrap_do_update_forwards_returning_fields_in_passthrough_path():
    from django.contrib.auth.models import Group

    from demo.models import SimpleConcurrentModel

    instance = SimpleConcurrentModel.objects.create(username="abc")
    captured = {}

    def fake_do_update(
        model_instance,
        base_qs,
        using,
        pk_val,
        values,
        update_fields,
        forced_update,
        returning_fields=None,
    ):
        captured["returning_fields"] = returning_fields
        return ["sentinel"]

    wrapped = instance._concurrencymeta.field._wrap_do_update(fake_do_update)
    result = wrapped(
        instance,
        Group._base_manager.using(instance._state.db),
        instance._state.db,
        instance.pk,
        [],
        None,
        False,
        returning_fields=["id"],
    )

    assert result == ["sentinel"]
    assert captured["returning_fields"] == ["id"]


@pytest.mark.django_db(transaction=False)
def test_wrap_do_update_returns_django6_shapes_for_no_values():
    from demo.models import SimpleConcurrentModel

    instance = SimpleConcurrentModel.objects.create(username="abc")

    def fake_do_update(
        model_instance,
        base_qs,
        using,
        pk_val,
        values,
        update_fields,
        forced_update,
        returning_fields=None,
    ):
        return True

    wrapped = instance._concurrencymeta.field._wrap_do_update(fake_do_update)
    base_qs = SimpleConcurrentModel._base_manager.using(instance._state.db)

    updated = wrapped(
        instance,
        base_qs,
        instance._state.db,
        instance.pk,
        [],
        None,
        False,
        returning_fields=[],
    )
    not_updated = wrapped(
        instance,
        base_qs,
        instance._state.db,
        -1,
        [],
        None,
        False,
        returning_fields=[],
    )

    assert updated == [()]
    assert not_updated == []


@pytest.mark.django_db(transaction=False)
def test_accepts_argument_handles_explicit_kwargs_missing_and_signature_errors(monkeypatch):
    # Explicit support for "returning_fields" must be detected.
    def explicit(returning_fields=None):
        return returning_fields

    # Generic **kwargs support is also valid because callers can pass
    # "returning_fields" safely.
    def kwargs_only(**kwargs):
        return kwargs

    # Function without either explicit arg or **kwargs is not compatible.
    def missing():
        return None

    assert _accepts_argument(explicit, "returning_fields")
    assert _accepts_argument(kwargs_only, "returning_fields")
    assert not _accepts_argument(missing, "returning_fields")

    # If signature introspection fails, the helper must fail safely and report
    # "not supported" instead of raising.
    def boom(_func):
        raise ValueError("signature unavailable")

    monkeypatch.setattr("concurrency.fields.inspect.signature", boom)
    assert not _accepts_argument(explicit, "returning_fields")


@pytest.mark.django_db(transaction=False)
def test_wrap_do_update_legacy_signature_passthrough_ignores_returning_fields():
    from django.contrib.auth.models import Group

    from demo.models import SimpleConcurrentModel

    instance = SimpleConcurrentModel.objects.create(username="abc")
    captured = {"called": False}

    # This fake function intentionally does NOT support "returning_fields",
    # emulating Django <6.0 _do_update signatures.
    def fake_do_update(model_instance, base_qs, using, pk_val, values, update_fields, forced_update):
        captured["called"] = True
        return "legacy-sentinel"

    wrapped = instance._concurrencymeta.field._wrap_do_update(fake_do_update)
    result = wrapped(
        instance,
        Group._base_manager.using(instance._state.db),
        instance._state.db,
        instance.pk,
        [],
        None,
        False,
        returning_fields=["id"],
    )

    # The wrapper must not forward "returning_fields" to legacy call targets.
    assert captured["called"] is True
    assert result == "legacy-sentinel"


@pytest.mark.django_db(transaction=False)
def test_wrap_do_update_legacy_signature_returns_bool_shapes_for_no_values():
    from demo.models import SimpleConcurrentModel

    instance = SimpleConcurrentModel.objects.create(username="abc")
    base_qs = SimpleConcurrentModel._base_manager.using(instance._state.db)

    # Legacy-compatible do_update implementation (no returning_fields argument).
    def fake_do_update(model_instance, base_qs, using, pk_val, values, update_fields, forced_update):
        return True

    wrapped = instance._concurrencymeta.field._wrap_do_update(fake_do_update)

    updated = wrapped(
        instance,
        base_qs,
        instance._state.db,
        instance.pk,
        [],
        None,
        False,
        returning_fields=["id"],
    )
    not_updated = wrapped(
        instance,
        base_qs,
        instance._state.db,
        -1,
        [],
        None,
        False,
        returning_fields=["id"],
    )

    # For legacy signatures, "no-values" shapes remain bools.
    assert updated is True
    assert not_updated is False


def test_pre_save_is_idempotent_for_double_add_on_new_instance():
    from demo.models import AutoIncConcurrentModel

    # New instances start from the default version=0.
    instance = AutoIncConcurrentModel(username="abc")
    version_field = instance._concurrencymeta.field

    # Django 6 can evaluate insert values twice; both calls are add=True.
    first_value = version_field.pre_save(instance, add=True)
    second_value = version_field.pre_save(instance, add=True)

    # The same version must be reused, otherwise first save() stores version=2.
    assert first_value == 1
    assert second_value == 1
    assert instance.version == 1


@pytest.mark.django_db(transaction=False)
def test_do_update_returns_expected_shape_when_callback_returns_false(monkeypatch):
    from demo.models import SimpleConcurrentModel
    from demo.util import attributes

    instance = SimpleConcurrentModel.objects.create(username="abc")

    # Simulate a stale in-memory object: DB row has a newer version.
    instance.version = 0

    # Keep callback behavior local to this test.
    monkeypatch.setattr(conf, "_callback", lambda _target: False)

    # Trigger the select_on_save path so we execute Django 6 list-return logic.
    with attributes((SimpleConcurrentModel._meta, "select_on_save", True)):
        updated = instance._do_update(
            SimpleConcurrentModel._base_manager.using(instance._state.db),
            instance._state.db,
            instance.pk,
            [(SimpleConcurrentModel._meta.get_field("username"), None, "def")],
            None,
            False,
            returning_fields=[],
        )

    # The not-updated shape is runtime-dependent: Django 6+ uses [] and older
    # versions use False.
    assert updated == _expected_not_updated_shape()


@pytest.mark.django_db(transaction=False)
def test_do_update_returns_expected_shape_when_callback_returns_true(monkeypatch):
    from demo.models import SimpleConcurrentModel

    instance = SimpleConcurrentModel.objects.create(username="abc")

    # Force version mismatch so the optimistic-lock filter does not match a row.
    instance.version = 0
    monkeypatch.setattr(conf, "_callback", lambda _target: True)

    updated = instance._do_update(
        SimpleConcurrentModel._base_manager.using(instance._state.db),
        instance._state.db,
        instance.pk,
        [(SimpleConcurrentModel._meta.get_field("username"), None, "def")],
        None,
        False,
        returning_fields=[],
    )

    # The callback "allow update" branch must map to each Django runtime's
    # expected truthy shape.
    assert updated == _expected_updated_shape()


@pytest.mark.django_db(transaction=False)
def test_do_update_select_on_save_returns_expected_shape_when_update_reports_empty(monkeypatch):
    from demo.models import SimpleConcurrentModel
    from demo.util import attributes

    instance = SimpleConcurrentModel.objects.create(username="abc")

    # Emulate databases that report "nothing updated" while the row still
    # exists. Django 6 returns [] for that condition, older runtimes report 0.
    # The wrapper should still convert this into a successful no-values shape.
    empty_update_result = [] if _django_core_supports_returning_fields() else 0
    monkeypatch.setattr(
        QuerySet,
        "_update",
        lambda self, values, *args, **kwargs: empty_update_result,
    )

    with attributes((SimpleConcurrentModel._meta, "select_on_save", True)):
        updated = instance._do_update(
            SimpleConcurrentModel._base_manager.using(instance._state.db),
            instance._state.db,
            instance.pk,
            [(SimpleConcurrentModel._meta.get_field("username"), None, "def")],
            None,
            False,
            returning_fields=[],
        )

    # If the row exists after an "empty" update result, select_on_save fallback
    # must treat the operation as successful.
    assert updated == _expected_updated_shape()
