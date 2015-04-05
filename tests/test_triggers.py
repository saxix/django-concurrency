# -*- coding: utf-8 -*-
import logging
from django.db import connections
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_list_triggers():
    conn = connections['default']
    assert conn.list_triggers() == [u'concurrency_demo_triggerconcurrentmodel_u',
                                    u'concurrency_demo_triggerconcurrentmodel_i']


@pytest.mark.django_db
def test_drop_triggers():
    conn = connections['default']
    target, triggers = list(conn.creation._triggers.items())[0]
    try:
        conn.drop_triggers()
        assert conn.list_triggers() == []
    finally:
        conn.creation._create_trigger(target)
