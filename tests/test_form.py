from django.forms.models import modelform_factory
import pytest
from concurrency.core import get_version_fieldname
from concurrency.exceptions import VersionError
from concurrency.forms import ConcurrentForm
from tests.util import with_all_models, unique_name


@with_all_models
@pytest.mark.django_db
def test_form_clean_on_add(model_class):
    """ form is valid
    """
    instance = model_class(username='name')
    Form = modelform_factory(model_class, ConcurrentForm)
    form = Form(data={}, instance=instance)
    assert form.is_valid()


@with_all_models
@pytest.mark.django_db
def test_form_clean_on_update(model_class):
    instance = model_class.objects.create(username=unique_name(20))
    Form = modelform_factory(model_class, ConcurrentForm)
    form = Form(data={}, instance=instance)
    assert form.is_valid()


@with_all_models
@pytest.mark.django_db
def test_tampering(model_class):
    instance = model_class.objects.create(username=unique_name(20))
    Form = modelform_factory(model_class, ConcurrentForm)
    version_field = get_version_fieldname(model_class)
    form = Form(data={}, instance=instance)
    data = form.initial
    data[version_field] = 101

    form = Form(data=data, instance=instance)
    with pytest.raises(VersionError):
        form.is_valid()


# class FormTests(TestCase):
#     def setUp(self):
#         self.obj = SimpleModel.objects.create(name='foo')
#
#     def test_conflict(self):
#         form = ConcurrentForm(instance=self.obj)
#         form = SimpleForm(data=form.initial, instance=self.obj)
#
#         refetch(self.obj).save()
#
#         with self.assertRaises(ConcurrentUpdate):
#             form.save()
#
#     def test_tampering(self):
#         """
# When messing with the version in the form, an exception should be
# raised
# """
#         form = SimpleForm(instance=self.obj)
#         data = form.initial
#         data['version'] = str(int(data['version']) + 1)
#         form = SimpleForm(data=data, instance=self.obj)
#
#         with self.assertRaises(ConcurrentUpdate):
#             form.save()
#
#     def test_omit(self):
#         form = SimpleForm(instance=self.obj)
#         data = form.initial
#         del data['version']
#         form = SimpleForm(data=data, instance=self.obj)
#         self.assertFalse(form.is_valid())
#
#     def test_field_is_hidden(self):
#         form = SimpleForm(instance=self.obj)
#         self.assertIn(
#             '<input id="id_version" name="version" type="hidden" value="0"',
#             form.as_p()
#         )
#
#     def test_actually_works(self):
#         form = SimpleForm(instance=self.obj)
#         data = form.initial
#         data['name'] = 'bar'
#         form = SimpleForm(data=data, instance=self.obj)
#         self.obj = form.save()
#         self.assertEqual(self.obj.name, 'bar')
#
#     def test_admin(self):
#         """
# VersionFields must be rendered as a readonly text input in the admin.
# """
#         from django.contrib.auth.models import User
#         User.objects.create_superuser(
#             username='foo',
#             password='foo',
#             email='foo@example.com'
#         )
#         c = Client()
#         c.login(username='foo', password='foo')
#         resp = c.get(
#             reverse('admin:tests_simplemodel_change', args=(self.obj.pk,))
#         )
#
#         self.assertIn(
#             b'<input id="id_version" name="version" readonly="readonly" type="text" value="0"',
#             resp.content
#         )
#
