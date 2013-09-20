from django.contrib.admin import site, ModelAdmin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from concurrency.admin import ConcurrentModelAdmin
from concurrency.forms import VersionFieldSigner
from concurrency.tests.base import AdminTestCase, SENTINEL
from concurrency.tests.models import TestModel1, TestModel0, ConcurrentModel


class TestConcurrentModelAdmin(AdminTestCase):
    def setUp(self):
        super(TestConcurrentModelAdmin, self).setUp()
        assert isinstance(site._registry[ConcurrentModel], ConcurrentModelAdmin)

    def test_standard_update(self):
        target, __ = ConcurrentModel.objects.get_or_create(dummy_char='aaa')
        url = reverse('admin:concurrency_concurrentmodel_change', args=[target.pk])
        res = self.app.get(url, user='sax')
        target = res.context['original']
        old_version = target.version
        form = res.form
        form['dummy_char'] = 'UPDATED'
        res = form.submit().follow()
        target = ConcurrentModel.objects.get(pk=target.pk)
        new_version = target.version
        self.assertGreater(new_version, old_version)

    def test_creation(self):
        url = reverse('admin:concurrency_concurrentmodel_add')
        res = self.app.get(url, user='sax')
        form = res.form
        form['dummy_char'] = 'CHAR'
        res = form.submit().follow()
        self.assertTrue(ConcurrentModel.objects.filter(dummy_char='CHAR').exists())
        self.assertGreater(ConcurrentModel.objects.get(dummy_char='CHAR').version, 0)

    def test_conflict(self):
        target, __ = ConcurrentModel.objects.get_or_create(dummy_char='aaa')
        url = reverse('admin:concurrency_concurrentmodel_change', args=[target.pk])
        res = self.app.get(url, user='sax')
        form = res.form

        target.save()  # create conflict here

        res = form.submit()
        self.assertIn('original', res.context)
        self.assertTrue(res.context['adminform'].form.errors,
                        res.context['adminform'].form.errors)
        self.assertIn(_('Record Modified'),
                      str(res.context['adminform'].form.errors),
                      res.context['adminform'].form.errors)


class TestAdminEdit(AdminTestCase):
    def setUp(self):
        super(TestAdminEdit, self).setUp()
        assert isinstance(site._registry[TestModel1], ModelAdmin)

    def _create_conflict(self, pk):
        u = TestModel1.objects.get(pk=pk)
        u.dummy_char = SENTINEL
        u.save()

    def test_creation(self):
        url = reverse('admin:concurrency_testmodel1_add')
        res = self.app.get(url, user='sax')
        form = res.form
        form['dummy_char'] = 'CHAR'
        res = form.submit().follow()
        self.assertTrue(TestModel1.objects.filter(dummy_char='CHAR').exists())
        self.assertGreater(TestModel1.objects.get(dummy_char='CHAR').version, 0)

    def test_creation_with_customform(self):
        url = reverse('admin:concurrency_testmodel1_add')
        res = self.app.get(url, user='sax')
        form = res.form
        form['username'] = 'username1'
        res = form.submit().follow()
        self.assertTrue(TestModel1.objects.filter(username='username1').exists())
        self.assertGreater(TestModel1.objects.get(username='username1').version, 0)

        #test no other errors are raised
        res = form.submit()
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Test model0 with this Username already exists.")

    def test_standard_update(self):
        target, __ = TestModel0.objects.get_or_create(username='aaa')
        url = reverse('admin:concurrency_testmodel0_change', args=[target.pk])
        res = self.app.get(url, user='sax')
        target = res.context['original']
        old_version = target.version
        form = res.form
        form['dummy_char'] = 'UPDATED'
        res = form.submit().follow()
        target = TestModel0.objects.get(pk=target.pk)
        new_version = target.version
        self.assertGreater(new_version, old_version)

    def test_conflict(self):
        target, __ = TestModel1.objects.get_or_create(username='aaa')
        url = reverse('admin:concurrency_testmodel1_change', args=[target.pk])
        res = self.app.get(url, user='sax')
        form = res.form

        target.save()  # create conflict here

        res = form.submit()
        self.assertIn('original', res.context)
        self.assertTrue(res.context['adminform'].form.errors,
                        res.context['adminform'].form.errors)
        self.assertIn(_('Record Modified'),
                      str(res.context['adminform'].form.errors),
                      res.context['adminform'].form.errors)

    def test_sanity_signer(self):
        target, __ = TestModel1.objects.get_or_create(username='aaa')
        url = reverse('admin:concurrency_testmodel1_change', args=[target.pk])
        res = self.app.get(url, user='sax')
        form = res.form
        version1 = int(str(form['version'].value).split(":")[0])
        form['version'] = VersionFieldSigner().sign(version1)
        form['date_field'] = 'esss2010-09-01'
        response = form.submit()
        self.assertIn('original', response.context)
        self.assertTrue(response.context['adminform'].form.errors,
                        response.context['adminform'].form.errors)
        form = response.context['adminform'].form
        version2 = int(str(form['version'].value()).split(":")[0])
        self.assertEqual(version1, version2)
