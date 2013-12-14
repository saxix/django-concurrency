# -*- coding: utf-8 -*-
from time import sleep
from django.core import signals
from django.db import connection, connections
from django.test import TestCase, TransactionTestCase
from concurrency.tests.models import TriggerConcurrentModel
# from django.test.utils import CaptureQueriesContext
from django.core.signals import request_started

# Register an event to reset saved queries when a Django request is started.
def reset_queries(**kwargs):
    for conn in connections.all():
        conn.queries = []
signals.request_started.connect(reset_queries)

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


class TriggerVersionFieldTest(TransactionTestCase):
    def test_success(self):
        # input('Starting')


        obj = TriggerConcurrentModel()
        assert obj.pk is None
        assert obj.version == 0
        sleep(1)
        obj = TriggerConcurrentModel.objects.create()
        assert obj.pk
        assert obj.version > 0

        obj, __ = TriggerConcurrentModel.objects.get_or_create(dummy_char='a')
        assert obj.pk
        assert obj.version > 0
        sleep(1)
        with CaptureQueriesContext(connection) as c:
            obj.save()
            v = obj.version
            print obj.version, v
            #assert v > 1
            #print c.captured_queries
            #assert len(c.captured_queries) == 1, c.captured_queries
            sleep(1)
            obj.save()
            print obj.version, v
            assert obj.version > v
            #print c.captured_queries

        # input('Waiting')
