# -*- coding: utf-8 -*-
import logging

from django.db import connections

import pytest
from demo.models import DropTriggerConcurrentModel, TriggerConcurrentModel  # noqa

from concurrency.triggers import drop_triggers, factory

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_list_triggers():
    conn = connections['default']

    assert factory(conn).get_list() == [
        u'concurrency_demo_droptriggerconcurrentmodel_version',
        u'concurrency_demo_triggerconcurrentmodel_version']


@pytest.mark.django_db
def test_get_trigger(monkeypatch):
    conn = connections['default']
    f = factory(conn)
    version_field = TriggerConcurrentModel._concurrencymeta.field
    trigger = f.get_trigger(version_field)
    assert trigger == 'concurrency_demo_triggerconcurrentmodel_version'

    monkeypatch.setattr(version_field, '_trigger_name', 'aaa')
    assert f.get_trigger(version_field) is None


@pytest.mark.skipif('connections["default"].vendor=="mysql"',
                    reason="Mysql is not able to drop tringger inside trasaction")
@pytest.mark.django_db
def test_drop_trigger():
    conn = connections['default']
    f = [f for f in DropTriggerConcurrentModel._meta.fields if f.name == 'version'][0]
    ret = factory(conn).drop(f)
    assert ret == [u'concurrency_demo_droptriggerconcurrentmodel_version']
    assert factory(conn).get_list() == [u'concurrency_demo_triggerconcurrentmodel_version']


@pytest.mark.skipif('connections["default"].vendor=="mysql"',
                    reason="Mysql is not able to drop tringger inside trasaction")
@pytest.mark.django_db
def test_drop_triggers(db):
    conn = connections['default']
    ret = drop_triggers('default')
    assert sorted([i[0].__name__ for i in ret['default']]) == ['DropTriggerConcurrentModel',
                                                               'TriggerConcurrentModel']
    assert factory(conn).get_list() == []
