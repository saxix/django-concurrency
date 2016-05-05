# -*- coding: utf-8 -*-
from django.core.signals import request_started
from django.db import IntegrityError, connections

import mock
import pytest
from demo.models import TriggerConcurrentModel
# Register an event to reset saved queries when a Django request is started.
from demo.util import nextname

from concurrency.exceptions import RecordModifiedError
from concurrency.utils import refetch


def reset_queries(**kwargs):
    for conn in connections.all():
        conn.queries = []


class CaptureQueriesContext(object):
    """
    Context manager that captures queries executed by the specified connection.
    """

    def __init__(self, connection):
        self.connection = connection

    def __iter__(self):
        return iter(self.captured_queries)

    def __getitem__(self, index):
        return self.captured_queries[index]

    def __len__(self):
        return len(self.captured_queries)

    @property
    def captured_queries(self):
        return self.connection.queries[self.initial_queries:self.final_queries]

    def __enter__(self):
        self.use_debug_cursor = self.connection.use_debug_cursor
        self.connection.use_debug_cursor = True
        self.initial_queries = len(self.connection.queries)
        self.final_queries = None
        request_started.disconnect(reset_queries)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.use_debug_cursor = self.use_debug_cursor
        request_started.connect(reset_queries)
        if exc_type is not None:
            return
        self.final_queries = len(self.connection.queries)


@pytest.mark.django_db
def test_trigger():
    instance = TriggerConcurrentModel()
    assert instance.pk is None
    assert instance.version == 0

    instance.username = next(nextname)
    instance.save()  # insert
    instance = refetch(instance)
    assert instance.version == 1

    instance.username = next(nextname)
    instance.save()  # update
    assert instance.version == 2

    instance.username = next(nextname)
    instance.save()  # update
    assert instance.version == 3

    instance.username = next(nextname)
    instance.save(refetch=True)  # update
    assert instance.version == 4

    copy = refetch(instance)
    copy.save()

    with pytest.raises(RecordModifiedError):
        instance.save()


@pytest.mark.django_db
def test_trigger_do_not_increase_version_if_error():
    instance = TriggerConcurrentModel()
    assert instance.pk is None
    assert instance.version == 0
    with mock.patch('demo.models.TriggerConcurrentModel.save', side_effect=IntegrityError):
        with pytest.raises(IntegrityError):
            instance.save()

    assert instance.version == 0
