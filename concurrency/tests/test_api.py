from unittest import skipIf
import django
from django.test import TestCase
from concurrency.api import (is_changed, get_revision_of_object,
                             get_version, get_object_with_version, disable_sanity_check)
from concurrency.tests.models import TestModel0, TestModelWithCustomSave


class ConcurrencyTestApi(TestCase):
    def test_is_changed(self):
        o1 = TestModel0.objects.create()
        o2 = TestModel0.objects.get(pk=o1.pk)
        self.assertFalse(is_changed(o1))
        o1.save()
        self.assertTrue(is_changed(o2))

    def test_get_revision_of_object(self):
        o1 = TestModel0.objects.create()
        self.assertEqual(get_revision_of_object(o1), o1.version)

    def test_get_version(self):
        o1 = TestModel0.objects.create()
        self.assertEqual(get_version(o1, o1.version), o1)

    def test_get_object_version(self):
        o1 = TestModel0.objects.create()
        self.assertEqual(get_object_with_version(TestModel0.objects, o1.pk, o1.version), o1)


    def test_patched_get_version(self):
        o1 = TestModel0.objects.create()
        self.assertEqual(o1.get_concurrency_version(o1.version), o1)

    def test_patched_get_object_version(self):
        o1 = TestModel0.objects.create()
        self.assertEqual(TestModel0.objects.get_object_with_version(o1.pk, o1.version), o1)

    def test_sanity_check(self):
        with self.settings(CONCURRENCY_SANITY_CHECK=True):
            with disable_sanity_check(TestModelWithCustomSave):
                m = TestModelWithCustomSave(username="New", last_name="1", version=1)
                self.assertEqual(2222, m.save())
