import pytest
from demo.models import Issue3TestModel, SimpleConcurrentModel
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.forms.models import modelform_factory
from django.forms.widgets import HiddenInput, TextInput
from django.test import TestCase, override_settings
from django.test.testcases import SimpleTestCase
from django.utils.encoding import smart_str
from django.utils.translation import gettext as _

from concurrency.exceptions import VersionError
from concurrency.forms import (
    ConcurrentForm,
    VersionField,
    VersionFieldSigner,
    VersionWidget,
)

__all__ = ["WidgetTest", "FormFieldTest", "ConcurrentFormTest"]


class DummySigner:
    def sign(self, value):
        return smart_str(value)

    def unsign(self, signed_value):
        return smart_str(signed_value)


class WidgetTest(TestCase):
    def test(self):
        w = VersionWidget()
        self.assertHTMLEqual(w.render("ver", None), '<input name="ver" type="hidden"/><div></div>')
        self.assertHTMLEqual(
            w.render("ver", 100),
            '<input name="ver" type="hidden" value="100"/><div>100</div>',
        )


class FormFieldTest(SimpleTestCase):
    def test_with_wrong_signer(self):
        with self.settings(CONCURRENCY_FIELD_SIGNER="invalid.Signer"):
            with pytest.raises(ImproperlyConfigured):
                VersionField()

    def test_with_dummy_signer(self):
        f = VersionField(signer=DummySigner())
        assert f.clean(1) == 1
        assert f.clean("1") == 1
        assert f.clean(None) == 0
        assert f.clean("") == 0
        with pytest.raises(VersionError):
            f.clean("aa:bb")
        with pytest.raises(VersionError):
            f.clean(1.5)

    def test(self):
        f = VersionField()
        assert f.clean(VersionFieldSigner().sign(1)) == 1
        assert f.clean(VersionFieldSigner().sign("1")) == 1
        assert f.clean(None) == 0
        assert f.clean("") == 0
        with pytest.raises(VersionError):
            f.clean("100")
        with pytest.raises(VersionError):
            f.clean(VersionFieldSigner().sign(1.5))


class ConcurrentFormTest(TestCase):
    def test_version(self):
        Form = modelform_factory(SimpleConcurrentModel, ConcurrentForm, exclude=("char_field",))  # noqa
        form = Form()
        assert isinstance(form.fields["version"].widget, HiddenInput)

    def test_clean(self):
        pass

    def test_dummy_signer(self):
        obj, __ = Issue3TestModel.objects.get_or_create(username="aaa")
        Form = modelform_factory(  # noqa
            Issue3TestModel,
            fields=("id", "revision"),
            form=type(
                "xxx",
                (ConcurrentForm,),
                {"revision": VersionField(signer=DummySigner())},
            ),
        )
        data = {"id": 1, "revision": obj.revision}
        form = Form(data, instance=obj)
        assert form.is_valid(), form.non_field_errors()

    def test_signer(self):
        Form = modelform_factory(Issue3TestModel, form=ConcurrentForm, exclude=("char_field",))  # noqa
        form = Form({"username": "aaa"})
        assert form.is_valid(), form.non_field_errors()

    def test_initial_value(self):
        Form = modelform_factory(  # noqa
            SimpleConcurrentModel,
            type("xxx", (ConcurrentForm,), {}),
            exclude=("char_field",),
        )
        form = Form({"username": "aaa"})
        self.assertHTMLEqual(
            str(form["version"]),
            '<input id="id_version" name="version" type="hidden" value="">',
        )
        assert form.is_valid(), form.non_field_errors()

    def test_initial_value_with_custom_signer(self):
        Form = modelform_factory(  # noqa
            Issue3TestModel,
            exclude=("char_field",),
            form=type(
                "xxx",
                (ConcurrentForm,),
                {"version": VersionField(signer=DummySigner())},
            ),
        )
        form = Form({"username": "aaa"})
        self.assertHTMLEqual(
            str(form["version"]),
            '<input type="hidden" value="" name="version" id="id_version" />',
        )
        assert form.is_valid(), form.non_field_errors()

    def test_tamperig(self):
        obj, __ = Issue3TestModel.objects.get_or_create(username="aaa")
        Form = modelform_factory(Issue3TestModel, ConcurrentForm, exclude=("char_field",))  # noqa
        data = {
            "username": "aaa",
            "last_name": None,
            "date_field": None,
            "char_field": None,
            "version": "abc",
            "id": 1,
            "revision": obj.revision,
        }
        form = Form(data, instance=obj)
        with pytest.raises(SuspiciousOperation):
            form.is_valid()

    def test_custom_name(self):
        Form = modelform_factory(Issue3TestModel, ConcurrentForm, exclude=("char_field",))  # noqa
        form = Form()
        assert isinstance(form.fields["version"].widget, TextInput)
        assert isinstance(form.fields["revision"].widget, HiddenInput)

    def test_save(self):
        obj, __ = Issue3TestModel.objects.get_or_create(username="aaa")

        obj_copy = Issue3TestModel.objects.get(pk=obj.pk)
        Form = modelform_factory(  # noqa
            Issue3TestModel,
            ConcurrentForm,
            fields=(
                "username",
                "last_name",
                "date_field",
                "char_field",
                "version",
                "id",
                "revision",
            ),
        )
        data = {
            "username": "aaa",
            "last_name": None,
            "date_field": None,
            "char_field": None,
            "version": "abc",
            "id": 1,
            "revision": VersionFieldSigner().sign(obj.revision),
        }
        form = Form(data, instance=obj)
        obj_copy.save()  # save

        assert not form.is_valid()
        assert _("Record Modified") in form.non_field_errors()

    def test_is_valid(self):
        obj, __ = Issue3TestModel.objects.get_or_create(username="aaa")
        Form = modelform_factory(  # noqa
            Issue3TestModel,
            ConcurrentForm,
            fields=(
                "username",
                "last_name",
                "date_field",
                "char_field",
                "version",
                "id",
                "revision",
            ),
        )
        data = {
            "username": "aaa",
            "last_name": None,
            "date_field": None,
            "char_field": None,
            "version": "abc",
            "id": 1,
            "revision": VersionFieldSigner().sign(obj.revision),
        }
        form = Form(data, instance=obj)
        obj.save()  # save again simulate concurrent editing
        with pytest.raises(ValueError, match="could not be changed because the data didn't validate."):
            form.save()


def test_disabled(db, settings):
    obj, __ = SimpleConcurrentModel.objects.get_or_create(username="aaa")
    Form = modelform_factory(SimpleConcurrentModel, ConcurrentForm, fields=("username", "id", "version"))  # noqa
    data = {
        "username": "aaa",
        "id": 1,
        "version": VersionFieldSigner().sign(obj.version),
    }
    form = Form(data, instance=obj)
    obj.save()  # save again simulate concurrent editing
    with override_settings(CONCURRENCY_ENABLED=False):
        obj2 = form.save()
        assert obj2.version == obj.version
