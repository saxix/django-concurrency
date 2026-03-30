from django.contrib.admin import AdminSite
from demo.models import SimpleConcurrentModel
from concurrency.admin import ConcurrentModelAdmin


class MockRequest:
    pass


class MockSite:
    pass


def test_admin_check_fields():
    class InvalidAdmin(ConcurrentModelAdmin):
        fields = ["username"]  # missing 'version'

    ma = InvalidAdmin(SimpleConcurrentModel, AdminSite())
    errors = ma.check()
    assert any(e.id == "concurrency.A001" for e in errors)


def test_admin_check_fieldsets():
    class InvalidAdmin(ConcurrentModelAdmin):
        fieldsets = [
            (None, {"fields": ["username"]}),
        ]  # missing 'version'

    ma = InvalidAdmin(SimpleConcurrentModel, AdminSite())
    errors = ma.check()
    assert any(e.id == "concurrency.A002" for e in errors)


def test_admin_check_valid_fieldsets():
    class ValidAdmin(ConcurrentModelAdmin):
        fieldsets = [
            (None, {"fields": ["username", "version"]}),
        ]

    ma = ValidAdmin(SimpleConcurrentModel, AdminSite())
    errors = ma.check()
    assert not any(e.id == "concurrency.A001" for e in errors)
    assert not any(e.id == "concurrency.A002" for e in errors)
