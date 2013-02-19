from django.test import TestCase
from concurrency.api import is_changed, get_revision_of_object
from concurrency.tests import TestModel0


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

