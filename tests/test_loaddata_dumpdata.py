import json
import logging
import os
from io import StringIO

import pytest
from demo.models import SimpleConcurrentModel
from django.core.management import call_command

logger = logging.getLogger(__name__)


@pytest.mark.django_db()
def test_dumpdata():
    SimpleConcurrentModel.objects.create()
    out = StringIO()
    call_command('dumpdata', 'demo', stdout=out)
    data = json.loads(out.getvalue())
    assert data


@pytest.mark.django_db(transaction=True)
def test_loaddata_fail():
    datafile = os.path.join(os.path.dirname(__file__), 'dumpdata.json')
    with open(datafile, 'r') as f:
        data = json.load(f)
    pk = data[0]['pk']

    call_command('loaddata', datafile, stdout=StringIO())

    assert SimpleConcurrentModel.objects.get(id=pk).username == 'loaded'
