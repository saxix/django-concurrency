# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import logging

import pytest
from django.test import TestCase

from concurrency.utils import ConcurrencyTestMixin
from demo.models import SimpleConcurrentModel

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestConcurrencyTestMixin(ConcurrencyTestMixin, TestCase):
    concurrency_model = SimpleConcurrentModel
