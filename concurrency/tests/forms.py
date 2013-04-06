import warnings
from django.core.exceptions import SuspiciousOperation
from django.forms.models import modelform_factory
from django.forms.widgets import HiddenInput, TextInput
from django.utils.encoding import smart_str
from django.test import TestCase
from concurrency.core import InconsistencyError
from concurrency.exceptions import VersionError
from concurrency.forms import ConcurrentForm, VersionField, VersionFieldSigner, VersionWidget
from concurrency.tests import TestModel0, TestIssue3Model
from django.test.testcases import SimpleTestCase
from django.utils.translation import ugettext as _


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

    def setUp(self):
        self.save_warnings_state()
        warnings.filterwarnings('ignore', category=DeprecationWarning,
                                module='django.core.validators')

    def tearDown(self):
        self.restore_warnings_state()

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
        Form = modelform_factory(TestModel0, ConcurrentForm)
        form = Form()
        self.assertIsInstance(form.fields['version'].widget, HiddenInput)

    def test_clean(self):
        pass

    def test_dummy_signer(self):
        obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
        Form = modelform_factory(TestIssue3Model, type('xxx', (ConcurrentForm,), {'revision': VersionField(signer=DummySigner())}))
        data = {'id': 1,
                'revision': obj.revision}
        form = Form(data, instance=obj)
        self.assertTrue(form.is_valid(), form.non_field_errors())

    def test_signer(self):
        Form = modelform_factory(TestIssue3Model, ConcurrentForm)
        form = Form({'username': 'aaa'})
        self.assertTrue(form.is_valid(), form.non_field_errors())

    def test_initial_value(self):
        Form = modelform_factory(TestModel0, type('xxx', (ConcurrentForm,), {}))
        form = Form({'username': 'aaa'})
        self.assertHTMLEqual(str(form['version']), '<input type="hidden" value="" name="version" id="id_version" />')
        self.assertTrue(form.is_valid(), form.non_field_errors())

    def test_initial_value_with_custom_signer(self):
        Form = modelform_factory(TestIssue3Model, type('xxx', (ConcurrentForm,), {'version': VersionField(signer=DummySigner())}))
        form = Form({'username': 'aaa'})
        self.assertHTMLEqual(str(form['version']), '<input type="hidden" value="" name="version" id="id_version" />')
        self.assertTrue(form.is_valid(), form.non_field_errors())

    def test_tamperig(self):
        obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
        Form = modelform_factory(TestIssue3Model, ConcurrentForm)
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
                'version': 'abc',
                'id': 1,
                'revision': VersionFieldSigner().sign(obj.revision)}
        form = Form(data, instance=obj)
        obj_copy.save() # save
        self.assertFalse(form.is_valid())
        self.assertIn(_('Record Modified'), form.non_field_errors())

    def test_is_valid(self):
        obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
        Form = modelform_factory(TestIssue3Model, ConcurrentForm)
        data = {'username': 'aaa',
                'last_name': None,
                'date_field': None,
                'char_field': None,
                'version': 'abc',
                'id': 1,
                'revision': VersionFieldSigner().sign(obj.revision)}
        form = Form(data, instance=obj)
        obj.save() # save again simulate concurrent editing
        self.assertRaises(ValueError, form.save)

    def test_form_is_valid(self):
        with self.settings(CONCURRECY_SANITY_CHECK=True):
            obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
            Form = modelform_factory(TestIssue3Model, ConcurrentForm)
            data = {'username': "a",
                    'revision': VersionFieldSigner().sign(1)}
            form = Form(data)
            self.assertRaises(InconsistencyError, form.is_valid)

    def test_signing(self):
        """ Do not accept version value if adding"""
        with self.settings(CONCURRECY_SANITY_CHECK=True):
            obj, __ = TestIssue3Model.objects.get_or_create(username='aaa')
            Form = modelform_factory(TestIssue3Model, ConcurrentForm)
            data = {'username': "a",
                    'revision': VersionFieldSigner().sign(1)}
            form = Form(data)
            self.assertRaises(InconsistencyError, form.is_valid)
