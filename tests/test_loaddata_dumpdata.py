# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import os
from six import StringIO

from django.core.management import call_command

import pytest
from demo.models import SimpleConcurrentModel

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
