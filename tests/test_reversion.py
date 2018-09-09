# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest
from demo.models import ReversionConcurrentModel
from reversion import add_to_revision, revisions, set_comment
from reversion.models import Version

try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.functional
def test_recover(admin_user, client):
    concurrentmodel = ReversionConcurrentModel.objects.create(username='USERNAME-OLD')
    with revisions.create_revision():
        set_comment("Initial revision")
        add_to_revision(concurrentmodel)

    ver = Version.objects.get_for_model(concurrentmodel).first()
    url = reverse('admin:demo_reversionconcurrentmodel_recover',
                  args=[concurrentmodel.pk])
    res = client.get(url, user=admin_user.username)
    res.form.submit().follow()

    concurrentmodel2 = ReversionConcurrentModel.objects.get(pk=concurrentmodel.pk)
    assert concurrentmodel2.username == ver.field_dict['username']
    assert concurrentmodel2.version > ver.field_dict['version']
