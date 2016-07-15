# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.contrib.auth.models import User

import pytest
from demo.models import ConditionalVersionModel, ConditionalVersionModelWithoutMeta

from concurrency.exceptions import RecordModifiedError
from concurrency.utils import refetch

logger = logging.getLogger(__name__)


@pytest.fixture
def user():
    return User.objects.get_or_create(username='username')[0]


@pytest.fixture
def instance(user):
    return ConditionalVersionModel.objects.get_or_create(field1='1',
                                                         user=user,
                                                         field2='1', field3='1')[0]


@pytest.fixture
def instance_no_meta(user):
    return ConditionalVersionModelWithoutMeta.objects.create(
        field1='1',
        user=user,
        field2='1', field3='1'
    )


@pytest.mark.django_db
def test_standard_save(instance):
    # only increment if checked field
    instance = refetch(instance)
    version1 = instance.get_concurrency_version()
    assert version1 == 1  # version2 > version1

    instance.field1 = '2'
    instance.save()
    version2 = instance.get_concurrency_version()
    assert version2 == 2  # version2 > version1

    instance.field3 = '3'
    instance.save()
    version3 = instance.get_concurrency_version()
    assert version3 == 2  # version3 == version2

    instance.user = None
    instance.save()
    version4 = instance.get_concurrency_version()
    assert version4 == 3  # version4 > version2


@pytest.mark.django_db(transaction=True)
def test_conflict(instance):
    # Scenario: batch change field present in ConcurrencyMeta.check_fields
    # the user is NOT ALLOWED to save
    batch_instance = instance.__class__.objects.get(pk=instance.pk)
    assert batch_instance.version == instance.version

    batch_instance.field1 = 'aaaa'
    batch_instance.save()

    with pytest.raises(RecordModifiedError):
        instance.save()


@pytest.mark.django_db(transaction=True)
def test_save_allowed(instance):
    # Scenario: batch change field NOT present in ConcurrencyMeta.check_fields
    # the user is ALLOWED to save
    batch_instance = instance.__class__.objects.get(pk=instance.pk)
    assert batch_instance.version == instance.version
    instance = refetch(instance)
    batch_instance = refetch(instance)

    batch_instance.field3 = 'aaaa'
    batch_instance.save()
    instance.save()


@pytest.mark.django_db(transaction=True)
def test_conflict_no_meta(instance_no_meta):
    # Scenario: batch change any field,
    # the user is NOT ALLOWED to save
    batch_instance = instance_no_meta.__class__.objects.get(pk=instance_no_meta.pk)
    assert batch_instance.version == instance_no_meta.version

    batch_instance.field1 = 'aaaa'
    batch_instance.save()

    with pytest.raises(RecordModifiedError):
        instance_no_meta.save()
