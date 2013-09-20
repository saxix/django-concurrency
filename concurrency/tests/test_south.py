# -*- coding: utf-8 -*-
from django.test import TestCase
from concurrency.fields import IntegerVersionField, AutoIncVersionField

__all__ = ['SouthTestCase']

try:
    from south.modelsinspector import can_introspect

    class SouthTestCase(TestCase):
        def test_south_can_introspect_integerversionfield(self):
            self.assertTrue(can_introspect(IntegerVersionField()))

        def test_south_can_introspect_autoincversionfield(self):
            self.assertTrue(can_introspect(AutoIncVersionField()))

except ImportError:
    class SouthTestCase(object):
        pass


