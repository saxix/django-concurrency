from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.forms.models import modelform_factory
from django.forms.widgets import HiddenInput, TextInput
from django.test import TestCase
from django.test.testcases import SimpleTestCase
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

import pytest
from demo.models import Issue3TestModel, SimpleConcurrentModel

from concurrency.exceptions import VersionError
from concurrency.forms import (
    ConcurrentForm, VersionField, VersionFieldSigner, VersionWidget
)

__all__ = ['WidgetTest', 'FormFieldTest', 'ConcurrentFormTest']


class DummySigner():
    def sign(self, value):
        return smart_str(value)

    def unsign(self, signed_value):
        return smart_str(signed_value)


class WidgetTest(TestCase):
    def test(self):
        w = VersionWidget()
        self.assertHTMLEqual(w.render('ver', None),
                             '<input name="ver" type="hidden"/><div></div>')
        self.assertHTMLEqual(w.render('ver', 100),
                             '<input name="ver" type="hidden" value="100"/><div>100</div>')


class FormFieldTest(SimpleTestCase):
    def test_with_wrong_signer(self):
        with self.settings(CONCURRENCY_FIELD_SIGNER='invalid.Signer'):
            with pytest.raises(ImproperlyConfigured):
                VersionField()

    def test_with_dummy_signer(self):
        f = VersionField(signer=DummySigner())
        self.assertEqual(1, f.clean(1))
        self.assertEqual(1, f.clean('1'))
        self.assertEqual(0, f.clean(None))
        self.assertEqual(0, f.clean(''))
        self.assertRaises(VersionError, f.clean, 'aa:bb')
        self.assertRaises(VersionError, f.clean, 1.5)

    def test(self):
        f = VersionField()
        self.assertEqual(1, f.clean(VersionFieldSigner().sign(1)))
        self.assertEqual(1, f.clean(VersionFieldSigner().sign('1')))
        self.assertEqual(0, f.clean(None))
        self.assertEqual(0, f.clean(''))
        self.assertRaises(VersionError, f.clean, '100')
        self.assertRaises(VersionError, f.clean, VersionFieldSigner().sign(1.5))


class ConcurrentFormTest(TestCase):
    def test_version(self):
        Form = modelform_factory(SimpleConcurrentModel, ConcurrentForm, exclude=('char_field',))
        form = Form()
        self.assertIsInstance(form.fields['version'].widget, HiddenInput)

    def test_clean(self):
        pass

    def test_dummy_signer(self):
        obj, __ = Issue3TestModel.objects.get_or_create(username='aaa')
        Form = modelform_factory(Issue3TestModel,
                                 fields=('id', 'revision'),
                                 form=type('xxx', (ConcurrentForm,), {'revision': VersionField(signer=DummySigner())}))
        data = {'id': 1,
                'revision': obj.revision}
        form = Form(data, instance=obj)
        self.assertTrue(form.is_valid(), form.non_field_errors())

    def test_signer(self):
        Form = modelform_factory(Issue3TestModel, form=ConcurrentForm,
                                 exclude=('char_field',))
        form = Form({'username': 'aaa'})
        self.assertTrue(form.is_valid(), form.non_field_errors())

    def test_initial_value(self):
        Form = modelform_factory(SimpleConcurrentModel, type('xxx', (ConcurrentForm,), {}), exclude=('char_field',))
        form = Form({'username': 'aaa'})
        self.assertHTMLEqual(str(form['version']), '<input type="hidden" value="" name="version" id="id_version" />')
        self.assertTrue(form.is_valid(), form.non_field_errors())

    def test_initial_value_with_custom_signer(self):
        Form = modelform_factory(Issue3TestModel, exclude=('char_field',),
                                 form=type('xxx', (ConcurrentForm,),
                                           {'version': VersionField(signer=DummySigner())}))
        form = Form({'username': 'aaa'})
        self.assertHTMLEqual(str(form['version']), '<input type="hidden" value="" name="version" id="id_version" />')
        self.assertTrue(form.is_valid(), form.non_field_errors())

    def test_tamperig(self):
        obj, __ = Issue3TestModel.objects.get_or_create(username='aaa')
        Form = modelform_factory(Issue3TestModel, ConcurrentForm, exclude=('char_field',))
        data = {'username': 'aaa',
                'last_name': None,
                'date_field': None,
                'char_field': None,
                'version': 'abc',
                'id': 1,
                'revision': obj.revision}
        form = Form(data, instance=obj)
        self.assertRaises(SuspiciousOperation, form.is_valid)

    def test_custom_name(self):
        Form = modelform_factory(Issue3TestModel, ConcurrentForm, exclude=('char_field',))
        form = Form()
        self.assertIsInstance(form.fields['version'].widget, TextInput)
        self.assertIsInstance(form.fields['revision'].widget, HiddenInput)

    def test_save(self):
        obj, __ = Issue3TestModel.objects.get_or_create(username='aaa')

        obj_copy = Issue3TestModel.objects.get(pk=obj.pk)
        Form = modelform_factory(Issue3TestModel, ConcurrentForm,
                                 fields=('username', 'last_name', 'date_field',
                                         'char_field', 'version', 'id', 'revision'))
        data = {'username': 'aaa',
                'last_name': None,
                'date_field': None,
                'char_field': None,
                'version': 'abc',
                'id': 1,
                'revision': VersionFieldSigner().sign(obj.revision)}
        form = Form(data, instance=obj)
        obj_copy.save()  # save

        self.assertFalse(form.is_valid())
        self.assertIn(_('Record Modified'), form.non_field_errors())

    def test_is_valid(self):
        obj, __ = Issue3TestModel.objects.get_or_create(username='aaa')
        Form = modelform_factory(Issue3TestModel, ConcurrentForm,
                                 fields=('username', 'last_name', 'date_field',
                                         'char_field', 'version', 'id', 'revision'))
        data = {'username': 'aaa',
                'last_name': None,
                'date_field': None,
                'char_field': None,
                'version': 'abc',
                'id': 1,
                'revision': VersionFieldSigner().sign(obj.revision)}
        form = Form(data, instance=obj)
        obj.save()  # save again simulate concurrent editing
        self.assertRaises(ValueError, form.save)
