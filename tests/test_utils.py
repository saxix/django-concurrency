# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging

import pytest
from django.test import TestCase

from demo.models import SimpleConcurrentModel

from concurrency.utils import ConcurrencyTestMixin

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestConcurrencyTestMixin(ConcurrencyTestMixin, TestCase):
    concurrency_model = SimpleConcurrentModel
