# -*- coding: utf-8 -*-
from concurrency.core import InconsistencyError
from concurrency.tests import DjangoAdminTestCase, TestModel0, TestModelWithCustomSave


class SettingsTest(DjangoAdminTestCase):

    def test_concurrecy_sanity_check(self):
        """
        Tests CONCURRECY_SANITY_CHECK settings
        """
        with self.settings(CONCURRECY_SANITY_CHECK=True):
            m = TestModelWithCustomSave(username="New", last_name="1", version=1)
            self.assertRaises(InconsistencyError, m.save)

        with self.settings(CONCURRECY_SANITY_CHECK=False):
            m = TestModelWithCustomSave(username="New", last_name="1", version=1)
            self.assertEqual(2222, m.save())
