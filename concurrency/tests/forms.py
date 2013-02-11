from django.core.exceptions import SuspiciousOperation
from django.forms.models import modelform_factory
from django.forms.widgets import HiddenInput, TextInput
from django.utils.encoding import smart_str
from django.utils.unittest.case import TestCase
from concurrency.forms import ConcurrentForm, VersionField, VersionFieldSigner
from concurrency.tests import TestModel0, TestIssue3Model


class DummySigner():
    def sign(self, value):
        return smart_str(value)

    def unsign(self, signed_value):
        return smart_str(signed_value)

class ConcurrentFormTest(TestCase):
    def test_version(self):
        Form = modelform_factory(TestModel0, ConcurrentForm)
        form = Form()
        self.assertIsInstance(form.fields['version'].widget, HiddenInput)

    def test_signer(self):
        obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
        Form = modelform_factory(TestIssue3Model, type('xxx',(ConcurrentForm,), {'revision': VersionField(signer=DummySigner())}))
        data = {'id': 1,
                'revision': obj.revision}
        form = Form(data, instance=obj)
        self.assertTrue(form.is_valid(), form.non_field_errors())

    def test_signer2(self):
        Form = modelform_factory(TestIssue3Model, ConcurrentForm)
        form = Form({'username': 'aaa'})
        self.assertTrue(form.is_valid(), form.non_field_errors())

    def test_creation_None_version(self):
        Form = modelform_factory(TestIssue3Model, type('xxx',(ConcurrentForm,), {}))
        data = {'username': 'aaaq',
                'last_name': None,
                'revision': VersionField().prepare_value(None)}
        form = Form(data)
        self.assertTrue(form.is_valid())
        obj = form.save()

    def test_creation_empty_version(self):
        Form = modelform_factory(TestIssue3Model, type('xxx',(ConcurrentForm,), {}))
        data = {'username': 'aaaq',
                'last_name': None,
                'revision': VersionField().prepare_value('')}
        form = Form(data)
        self.assertTrue(form.is_valid())
        obj = form.save()

    def test_creation_0_version(self):
        Form = modelform_factory(TestIssue3Model, type('xxx',(ConcurrentForm,), {}))
        data = {'username': 'aaa',
                'revision': VersionField().prepare_value(0)}
        form = Form(data)
        self.assertTrue(form.is_valid())
        obj = form.save()

    def test_creation_empty_version2(self):
        obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
        Form = modelform_factory(TestIssue3Model, type('xxx',(ConcurrentForm,), {'revision': VersionField(signer=DummySigner())}))
        data = {'id': 1,
                'revision': ''}
        form = Form(data, instance=obj)
        self.assertTrue(form.is_valid(), form.non_field_errors())

    def test_tamperig(self):
        obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
        Form = modelform_factory(TestIssue3Model, ConcurrentForm)
        data = {'username': 'aaa',
                'last_name': None,
                'date_field': None,
                'char_field': None,
                'version': u'abc',
                'id': 1,
                'revision': obj.revision}
        form = Form(data, instance=obj)
        self.assertRaises(SuspiciousOperation, form.is_valid)

    def test_custom_name(self):
        Form = modelform_factory(TestIssue3Model, ConcurrentForm)
        form = Form()
        self.assertIsInstance(form.fields['version'].widget, TextInput)
        self.assertIsInstance(form.fields['revision'].widget, HiddenInput)

    def test_save(self):
        obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
        obj_copy = TestIssue3Model.objects.get(pk=obj.pk)
        Form = modelform_factory(TestIssue3Model, ConcurrentForm)
        data = {'username': 'aaa',
                'last_name': None,
                'date_field': None,
                'char_field': None,
                'version': u'abc',
                'id': 1,
                'revision': VersionFieldSigner().sign(obj.revision)}
        form = Form(data, instance=obj)
        obj_copy.save() # save
        self.assertFalse(form.is_valid())
        self.assertIn('Record Modified', form.non_field_errors())

    def test_is_valid(self):
        obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
        Form = modelform_factory(TestIssue3Model, ConcurrentForm)
        data = {'username': 'aaa',
                'last_name': None,
                'date_field': None,
                'char_field': None,
                'version': u'abc',
                'id': 1,
                'revision': VersionFieldSigner().sign(obj.revision)}
        form = Form(data, instance=obj)
        obj.save() # save again simulate concurrent editing
        self.assertRaises(ValueError, form.save)

