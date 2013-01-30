# -*- coding: utf-8 -*-
"""
Created on 09/giu/2009

@author: sax
"""
import logging
import time
import datetime
from django.contrib.auth.models import User
from django.forms.models import modelform_factory
from django.test import TestCase
from concurrency.core import RecordModifiedError
from concurrency.core import apply_concurrency_check
from concurrency.fields import IntegerVersionField
from concurrency.tests.models import TestModel0, TestModel1, TestModel2, TestModel3, TestModel0_Proxy, TestModelUser, TestAbstractModel0, TestModelGroup, TestModelWithCustomSave, TestIssue3Model, ModelWithCustomSave, TestModelGroupWithCustomSave
from concurrency.utils import ConcurrencyTestMixin
# from concurrency.tests.models import *


logger = logging.getLogger('tests.concurrency')
logger.setLevel(logging.DEBUG)


class ConcurrencyError(Exception):
    pass


class ConcurrencyTest0(ConcurrencyTestMixin, TestCase):
    concurrency_model = TestModel0
    concurrency_kwargs = {'username': 'test'}

    def setUp(self):
        super(ConcurrencyTest0, self).setUp()
        self._unique_field_name = 'username'
        self._get_target()
        setattr(self.TARGET.__class__, '_get_test_revision_number',
                ConcurrencyTest0._get_REVISION_NUMBER)

    def _get_target(self):
        self.TARGET = TestModel0(username="New", last_name="1")

    @staticmethod
    def _get_REVISION_NUMBER(obj):
        revision_field = obj.RevisionMetaInfo.field
        value = getattr(obj, revision_field.attname)
        return value

    def _check_save(self, obj):
        return obj.save()

    def _get_form_data(self, **kwargs):
        data = {}
        data.update(**kwargs)
        return data

    def test_standard_insert(self):
        logger.debug("Created Object_1")
        a = self.TARGET.__class__(**self.concurrency_kwargs)
        v = a._get_test_revision_number()
        logger.debug("Now Object_1.version is %s " % v)
        assert bool(v) is False, "version is not null %s" % v
        a.save()
        logger.debug("Object_1 saved...now version is %s " % a._get_test_revision_number())
        self.assertTrue(a.pk > 0)
        v2 = a._get_test_revision_number()
        assert v2 != v, "same or lower version after insert (%s,%s)" % (a._get_test_revision_number(), v)
        b = self.TARGET.__class__.objects.get(pk=a.pk)
        self.assertEqual(a._get_test_revision_number(), b._get_test_revision_number())

    def test_concurrency(self):
        logger.debug("Created Object_1")
        a = self.TARGET
        self._check_save(a)
        logger.debug("Object_1 saved...now version is %s " % a._get_test_revision_number())
        a_pk = a.pk

        a = self.TARGET.__class__.objects.get(pk=a_pk)
        v = a._get_test_revision_number()
        logger.debug("reloaded...now version is %s " % v)

        b = self.TARGET.__class__.objects.get(pk=a_pk)
        assert a._get_test_revision_number() == b._get_test_revision_number(), "got same row with different version"
        time.sleep(2)
        a.last_name = "pippo"
        self._check_save(a)
        logger.debug("updated...now version is %s " % a._get_test_revision_number())
        assert a._get_test_revision_number() != v, "same version after update (%s,%s)" % (a.version, v)
        self.assertRaises(RecordModifiedError, b.save)

    def test_concurrency_no_values(self):
        logger.debug("Created Object_1")
        t = self.TARGET.__class__()
        assert bool(t._get_test_revision_number()) is False, "version is not null %s" % t._get_test_revision_number()
        t.save()
        self.assertTrue(t.pk > 0)
        self.assertNotEqual(t.version, self.TARGET.RevisionMetaInfo.field.get_default())
        self.assertTrue(bool(t.version))

    def test_force_update(self):
        logger.debug("Created Object_1")
        t = self.TARGET.__class__()
        self.assertRaises(Exception, t.save, force_update=True)

    def test_force_insert(self):
        logger.debug("Created Object_1")
        t = self.TARGET.__class__(**self.concurrency_kwargs)
        assert bool(t._get_test_revision_number()) is False, "version is not null %s" % t._get_test_revision_number()
        t.save(force_insert=True)
        self.assertTrue(t.pk > 0)
        self.assertTrue(t._get_test_revision_number())

    def test_concurrency_manager_list(self):
        logger.debug("Start Test")
        # test di concorrenza con list(queryset)
        for i in xrange(10, 13):
            self.TARGET.__class__.objects.get_or_create(**{self._unique_field_name: "model %s" % i})

        prima_serie = list(self.TARGET.__class__.objects.all())
        seconda_serie = list(self.TARGET.__class__.objects.all())

        for el in prima_serie:
            el.last_name = "model %s 2^" % el.pk
            el.save()

        for el in seconda_serie:
            el.last_name = "model %s 3^" % el.pk
            self.assertRaises(RecordModifiedError, el.save)

    def test_concurrency_manager_get_item(self):
        """ test di concorrenza con list(queryset) """
        logger.debug("Start Test")
        for i in xrange(3):
            self.TARGET.__class__.objects.get_or_create(**{self._unique_field_name: "model %s" % i})

        prima_serie = self.TARGET.__class__.objects.all()
        seconda_serie = self.TARGET.__class__.objects.all()

        a = prima_serie[1]
        b = seconda_serie[1]
        a.last_name = "model %s 2^" % a.pk
        self._check_save(a)

        b.last_name = "model %s 3^" % b.pk
        self.assertRaises(RecordModifiedError, b.save)

    def test_form_save(self):
        formClass = modelform_factory(self.TARGET.__class__)
        original_version = self.TARGET._get_test_revision_number()
        version_field_name = self.TARGET.RevisionMetaInfo.field.name

        form = formClass(self._get_form_data(**{version_field_name: original_version}),
                         instance=self.TARGET)

        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertTrue(obj.pk)
        # self.assertGreater(obj._get_test_revision_number(), original_version)
        self.assertNotEqual(obj._get_test_revision_number(), original_version)

        form = formClass(self._get_form_data(**{version_field_name: obj._get_test_revision_number()}),
                         instance=obj)
        self.assertTrue(form.is_valid(), form.errors)
        pre_save_version = obj._get_test_revision_number()
        obj_after = form.save()

        self.assertTrue(obj_after.pk)
        self.assertNotEqual(obj_after._get_test_revision_number(), pre_save_version)
        self.assertTrue(bool(obj_after._get_test_revision_number()), "'%s'" % obj_after._get_test_revision_number())


# class DateConcurrencyTest1(ConcurrencyTest0):
#     concurrency_model = DateConcurrentModel
#
#     def _get_target(self):
#         self.TARGET = DateConcurrentModel(char_field="New", last_name="1")


class ConcurrencyTest1(ConcurrencyTest0):
    concurrency_model = TestModel1

    def _get_target(self):
        self.TARGET = TestModel1(char_field="New", last_name="1")

    def test_force_update(self):
        from django.db import DatabaseError

        t = self.TARGET.__class__()
        self.assertRaises(DatabaseError, t.save, force_update=True)


class ConcurrencyTest2(ConcurrencyTest0):
    concurrency_model = TestModel2

    def _get_target(self):
        self.TARGET = TestModel2(char_field="New", last_name="1")

    def test_force_update(self):
        from django.db import DatabaseError

        t = self.TARGET.__class__()
        logger.debug("Object pk: %s version:%s", t.pk, t._get_test_revision_number())
        self.assertRaises(DatabaseError, t.save, force_update=True)


class ConcurrencyTest3(ConcurrencyTest0):
    concurrency_model = TestModel3

    def setUp(self):
        super(ConcurrencyTest3, self).setUp()

    def _get_target(self):
        p, isnew = TestModel2.objects.get_or_create(char_field="New", last_name=str(time.time()))
        self.TARGET = TestModel3(char_field="New", last_name="1", fk=p)

    def test_force_update(self):
        from django.db import DatabaseError

        t = self.TARGET.__class__()
        self.assertRaises(DatabaseError, t.save, force_update=True)

    def test_concurrency(self):
        a = self.TARGET
        self._check_save(a)
        a_pk = a.pk

        a = self.TARGET.__class__.objects.get(pk=a_pk)
        v = a._get_test_revision_number()
        logger.debug("reloaded...now version is %s " % v)

        b = self.TARGET.__class__.objects.get(pk=a_pk)
        assert a.version == b.version, "got same row with different version"
        time.sleep(1)
        a.last_name = "pippo"
        self._check_save(a)
        logger.debug("updated...now version is %s " % a._get_test_revision_number())
        assert a.version > v, "same or lower version after update (%s,%s)" % (a._get_test_revision_number(), v)
        self.assertRaises(RecordModifiedError, b.save)


class ConcurrencyTest4(ConcurrencyTest0):
    concurrency_model = TestModel2

    def _get_target(self):
        self.TARGET = TestModel2(char_field="New", last_name="1")

    def test_manager(self):
        p1, isnew = TestModel2.objects.get_or_create(pk=1001, char_field="New", last_name="1")

        assert isnew is True
        p2, isnew = TestModel3.objects.get_or_create(pk=1002, char_field="New", last_name="1", fk=p1)
        assert isnew is True

        p1.save()
        p2.save()


class ConcurrencyTest0_Proxy(ConcurrencyTest0):
    def _get_target(self):
        self.TARGET = TestModel0_Proxy(char_field="New", last_name="1")

    def test_force_update(self):
        t = self.TARGET.__class__()
        t.save(force_update=True)
        t1 = TestModel0.objects.get(pk=t.pk)
        self.assertEqual(t.pk, t1.pk)


class ConcurrencyTest2_Proxy(ConcurrencyTest2):
    def _get_target(self):
        self.TARGET = TestModel2(char_field="New", last_name="1")


class ConcurrencyTest5(ConcurrencyTest0):
    def _get_target(self):
        self.TARGET = TestAbstractModel0(char_field="New", last_name="1")


class ConcurrencyTestModelUser(ConcurrencyTest0):
    concurrency_model = TestModelUser

    def _get_target(self):
        self.TARGET = TestModelUser(username="ConcurrencyTestModelUser")

    def _check_save(self, obj):
        obj.save()
        self.assertTrue(obj.version)

    def _get_form_data(self, **kwargs):
        data = {
            'last_login': datetime.datetime.today(),
            'date_joined': datetime.datetime.today(),
            'password': '123',
            'username': 'ConcurrencyTestModelUser'}
        data.update(**kwargs)
        return data


class ConcurrencyTestExistingModelGroup(ConcurrencyTest0):
    concurrency_model = User
    concurrency_kwargs = {'username': 'test'}
    apply_concurrency_check(User, 'version', IntegerVersionField)

    def setUp(self):
        super(ConcurrencyTestExistingModelGroup, self).setUp()
        self._unique_field_name = 'username'

    def _get_target(self):
        self.TARGET = User(username="aaa")

    def _get_form_data(self, **kwargs):
        data = {'username': 'aaaa', 'password': "123", 'last_login': '2000-01-01', 'date_joined': '2000-01-01'}
        data.update(**kwargs)
        return data


class ConcurrencyTestExistingModel(ConcurrencyTest0):
    """

    """
    apply_concurrency_check(TestModelGroup, 'version', IntegerVersionField)

    def setUp(self):
        super(ConcurrencyTestExistingModel, self).setUp()
        self._unique_field_name = 'name'

    def _get_target(self):
        self.TARGET = TestModelGroup(name="aaa")

    def _get_form_data(self, **kwargs):
        data = {
            'last_login': datetime.datetime.today(),
            'date_joined': datetime.datetime.today(),
            'password': '123',
            'name': 'aaa',
            'username': 'aaa'}
        data.update(**kwargs)
        return data


class ConcurrencyTestModelWithCustomSave(ConcurrencyTest0):
    def _get_target(self):
        self.TARGET = TestModelWithCustomSave(username="xxx", last_name="1")

    def _check_save(self, obj):
        self.assertEqual(obj.save(), 2222)


class ConcurrencyTestExistingModelWithCustomSave(ConcurrencyTest0):
    version = IntegerVersionField()
    version.contribute_to_class(TestModelGroupWithCustomSave, 'version')

    def setUp(self):
        super(ConcurrencyTestExistingModelWithCustomSave, self).setUp()
        self._unique_field_name = 'name'

    def _get_target(self):
        self.TARGET = TestModelGroupWithCustomSave(name="aaa")

    def _check_save(self, obj):
        ret = obj.save()
        self.assertEqual(ret, 2222)
        self.assertTrue(obj.version)

    def _get_form_data(self, **kwargs):
        data = {
            'last_login': datetime.datetime.today(),
            'date_joined': datetime.datetime.today(),
            'password': '123',
            'name': 'bbb',
            'username': 'bbb'}
        data.update(**kwargs)
        return data


class TestIssue3(ConcurrencyTest0):
    def _get_target(self):
        self.TARGET = TestIssue3Model()


class TestAbstractModelWithCustomSave(ConcurrencyTest0):
    concurrency_model = ModelWithCustomSave

    def _get_target(self):
        self.TARGET = ModelWithCustomSave(username="New", last_name="1")

    def _check_save(self, obj):
        ret = obj.save()
        self.assertSequenceEqual(ret, ('ModelWithCustomSave', 'AbstractModelWithCustomSave'))
        self.assertTrue(obj.version)
