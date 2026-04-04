import pytest
import mock
from concurrency.fields import class_prepared_concurrency_handler, filter_fields
from concurrency.forms import VersionWidget, SignedValue, VersionFieldSigner
from demo.models import ConditionalVersionModel, Anything


def test_fields_invalid_config():
    class MockMeta:
        check_fields = ["a"]
        ignore_fields = ["b"]

    class MockModel:
        ConcurrencyMeta = MockMeta
        _concurrencymeta = mock.Mock()
        _meta = mock.Mock()

    with pytest.raises(ValueError, match="Cannot set both 'check_fields' and 'ignore_fields'"):
        class_prepared_concurrency_handler(MockModel)


def test_filter_fields_generic_fk():
    class MockField:
        concrete = True
        is_relation = True
        related_model = None

    assert filter_fields(None, MockField) is False


def test_filter_fields_m2m_new_instance():
    class MockField:
        concrete = True
        is_relation = True
        related_model = mock.Mock()
        many_to_many = True

    class MockInstance:
        pk = None

    assert filter_fields(MockInstance, MockField) is False


def test_version_widget_signed_value():
    widget = VersionWidget()
    sv = SignedValue("123:abc")
    rendered = widget.render("version", sv)
    assert "<div>123</div>" in rendered


def test_version_field_signer_empty():
    signer = VersionFieldSigner()
    assert signer.sign("") is None
    assert signer.sign(None) is None


@pytest.mark.django_db
def test_conditional_version_field_ignore_fields(monkeypatch):
    # ConditionalVersionModel with ignore_fields
    instance = ConditionalVersionModel(field1="a", field2="b")
    monkeypatch.setattr(instance._concurrencymeta, "ignore_fields", ["field1"])
    monkeypatch.setattr(instance._concurrencymeta, "check_fields", None)

    h1 = instance._concurrencymeta.field._get_hash(instance)
    instance.field1 = "c"
    h2 = instance._concurrencymeta.field._get_hash(instance)
    assert h1 == h2  # field1 ignored


@pytest.mark.django_db
def test_conditional_version_field_m2m():
    from demo.models import ConditionalVersionModelWithoutMeta  # noqa: PLC0415

    m = ConditionalVersionModelWithoutMeta.objects.create()
    a = Anything.objects.create(name="a", a_relation=m)
    m.anythings.add(a)

    h1 = m._concurrencymeta.field._get_hash(m)
    assert h1 is not None
