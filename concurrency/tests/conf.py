# -*- coding: utf-8 -*-
from django.test import TestCase
from concurrency.core import InconsistencyError
from concurrency.tests.models import TestModelWithCustomSave


# class SettingsTest(DjangoAdminTestCase):
class SettingsTest(TestCase):

    def test_concurrecy_sanity_check(self):
        """
        Tests CONCURRENCY_SANITY_CHECK settings
        """
        with self.settings(CONCURRENCY_SANITY_CHECK=True):
            m = TestModelWithCustomSave(username="New", last_name="1", version=1)
            self.assertRaises(InconsistencyError, m.save)

        with self.settings(CONCURRENCY_SANITY_CHECK=False):
            m = TestModelWithCustomSave(username="New", last_name="1", version=1)
            self.assertEqual(2222, m.save())
