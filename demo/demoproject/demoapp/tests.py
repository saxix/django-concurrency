# -*- coding: utf-8 -*-
import StringIO
import os
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django_webtest import WebTest
from concurrency.api import disable_concurrency
from demoproject.demoapp.models import DemoModel

try:
    from import_export.admin import ImportExportMixin
    import csv

    class TestAdminEdit(WebTest):

        def setUp(self):
            self.user = User.objects.get_or_create(is_superuser=True,
                                       is_staff=True,
                                       is_active=True,
                                       email='sax@example.com',
                                       username='sax')

        def test_export_csv(self):
            for i in range(1, 10):
                DemoModel.objects.get_or_create(char=str(i), integer=i)

            url = reverse('admin:demoapp_demomodel_changelist')
            res = self.app.get(url, user='sax')
            res = res.click(_("Export"))
            res.form['file_format'] = 0
            res = res.form.submit()
            buffer = StringIO.StringIO(res.body)
            c = csv.reader(buffer)
            list(c)

        def get_file_to_upload(self, filename):
            here = os.path.dirname(__file__)
            filepath = os.path.join(here, "fixtures", filename)
            return open(filepath).read()

        def test_import_csv_no_version(self):
            url = reverse('admin:demoapp_demomodel_changelist')
            res = self.app.get(url, user='sax')
            res = res.click(_("Import"))
            res.form['import_file'] = ("import_file2",
                                       self.get_file_to_upload("data_no_version.csv"))
            res.form['input_format'] = 0
            res = res.form.submit()
            res = res.form.submit()

        def test_import_csv_with_version(self):
            url = reverse('admin:demoapp_demomodel_changelist')
            res = self.app.get(url, user='sax')
            res = res.click(_("Import"))
            with disable_concurrency(DemoModel):
                res.form['import_file'] = ("import_file2",
                                           self.get_file_to_upload("data_with_version.csv"))
                res.form['input_format'] = 0
                res = res.form.submit()
                res = res.form.submit()



except:
    pass
