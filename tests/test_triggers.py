# -*- coding: utf-8 -*-
import logging
from django.db import connections
import pytest
from concurrency.triggers import factory
from demo.models import DropTriggerConcurrentModel

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_list_triggers():
    conn = connections['default']

    assert factory(conn).list() == [
        u'concurrency_demo_droptriggerconcurrentmodel_version__i',
        u'concurrency_demo_droptriggerconcurrentmodel_version__u',
        u'concurrency_demo_triggerconcurrentmodel_version__i',
        u'concurrency_demo_triggerconcurrentmodel_version__u']


@pytest.mark.django_db
def test_drop_triggers():
    conn = connections['default']
    f = [f for f in DropTriggerConcurrentModel._meta.fields if f.name == 'version'][0]
    ret = factory(conn).drop(f)
    assert ret == [u'concurrency_demo_droptriggerconcurrentmodel_version__i',
                   u'concurrency_demo_droptriggerconcurrentmodel_version__u']
    assert factory(conn).list() == [u'concurrency_demo_triggerconcurrentmodel_version__i',
                                    u'concurrency_demo_triggerconcurrentmodel_version__u']
