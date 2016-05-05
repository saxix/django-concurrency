import sys

from django import db
from django.db import transaction

import pytest
from demo.models import TriggerConcurrentModel
from demo.util import concurrently

from concurrency.exceptions import RecordModifiedError
from concurrency.utils import refetch
from conftest import skippypy


@skippypy
@pytest.mark.django_db(transaction=True)
def test_threads():
    if db.connection.vendor == 'sqlite':
        pytest.skip("in-memory sqlite db can't be used between threads")

    obj = TriggerConcurrentModel.objects.create()
    transaction.commit()

    @concurrently(25)
    def run():
        for i in range(5):
            while True:
                x = refetch(obj)
                transaction.commit()
                x.count += 1
                try:
                    x.save()
                    transaction.commit()
                except RecordModifiedError:
                    # retry
                    pass
                else:
                    break

    run()
    assert refetch(obj).count == 5 * 25
