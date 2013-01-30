from django.forms.models import modelform_factory, model_to_dict
from django.forms.widgets import HiddenInput, TextInput
from django.utils.unittest.case import TestCase
from concurrency.forms import ConcurrentForm
from concurrency.tests import TestModel0, TestIssue3Model


class ConcurrentFormTest(TestCase):

    def test_version(self):
        Form = modelform_factory(TestModel0, ConcurrentForm)
        form = Form()
        self.assertIsInstance(form.fields['version'].widget, HiddenInput)

    def test_custom_name(self):
        Form = modelform_factory(TestIssue3Model, ConcurrentForm)
        form = Form()
        self.assertIsInstance(form.fields['version'].widget, TextInput)
        self.assertIsInstance(form.fields['revision'].widget, HiddenInput)

    def test_save(self):
        obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
        Form = modelform_factory(TestIssue3Model, ConcurrentForm)
        form = Form(model_to_dict(obj), instance=obj)
        obj.save() # save again simulate concurrent editing
        self.assertFalse(form.is_valid())
        self.assertIn('Record Modified', form.non_field_errors())

    def test_is_valid(self):
        obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
        Form = modelform_factory(TestIssue3Model, ConcurrentForm)
        form = Form(model_to_dict(obj), instance=obj)
        obj.save() # save again simulate concurrent editing
        self.assertRaises(ValueError, form.save)
