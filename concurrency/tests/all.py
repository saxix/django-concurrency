# -*- coding: utf-8 -*-
'''
Created on 09/giu/2009

@author: sax
'''
import logging
import time
import datetime
from django.forms.models import modelform_factory
from django.test import TestCase
from concurrency.core import RecordModifiedError
from .models import *


logger = logging.getLogger('tests.concurrency')
logger.setLevel(logging.DEBUG)


class ConcurrencyError(Exception):
    pass


class ConcurrencyTest0(TestCase):
    def setUp(self):
        super(ConcurrencyTest0, self).setUp()

        #        transaction.enter_transaction_management()
        #        transaction.managed(True)
        #        connection.close()
        self._unique_field_name = 'username'
        self.TARGET = TestModel0(username="New", last_name="1")

    def _check_save(self, obj):
        return obj.save()

    def _get_form_data(self, **kwargs):
        data = {}
        data.update(**kwargs)
        return data

    #    def tearDown(self):
    #        super(ConcurrencyTest0, self).tearDown()
    #        transaction.rollback()
    #        transaction.leave_transaction_management()

    def test_standard_insert(self):
        logger.debug("Created Object_1")
        a = self.TARGET.__class__(username='standard_insert')
        v = a.version
        logger.debug("Now Object_1.version is %s " % v)
        assert bool(v) is False, "version is not null %s" % v
        a.save()
        logger.debug("Object_1 saved...now version is %s " % a.version)
        self.assertTrue(a.pk > 0)
        assert a.version != v, "same or lower version after insert (%s,%s)" % (a.version, v)
        b = self.TARGET.__class__.objects.get(pk=a.pk)
        self.assertEqual(a.version, b.version)

    def test_concurrency(self):
        logger.debug("Created Object_1")
        a = self.TARGET
        self._check_save(a)
        logger.debug("Object_1 saved...now version is %s " % a.version)
        id = a.pk

        a = self.TARGET.__class__.objects.get(pk=id)
        v = a.version
        logger.debug("reloaded...now version is %s " % a.version)

        b = self.TARGET.__class__.objects.get(pk=id)
        assert a.version == b.version, "got same row with different version"
        time.sleep(2)
        a.last_name = "pippo"
        self._check_save(a)
        logger.debug("updated...now version is %s " % a.version)
        assert a.version != v, "same or lower version after update (%s,%s)" % (a.version, v)
        self.assertRaises(RecordModifiedError, b.save)

    def test_concurrency_no_values(self):
        logger.debug("Created Object_1")
        t = self.TARGET.__class__()
        assert bool(t.version) is False, "version is not null %s" % t.version
        t.save()
        self.assertTrue(t.pk > 0)
        self.assertGreater(t.version, 0)

    def test_force_update(self):
        logger.debug("Created Object_1")
        t = self.TARGET.__class__()
        self.assertRaises(Exception, t.save, force_update=True)

    def test_force_insert(self):
        logger.debug("Created Object_1")
        t = self.TARGET.__class__(username='empty')
        assert bool(t.version) is False, "version is not null %s" % t.version
        t.save(force_insert=True)
        self.assertTrue(t.pk > 0)
        self.assertTrue(t.version)

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
        original_version = self.TARGET.version
        form = formClass(self._get_form_data(version=original_version), instance=self.TARGET)

        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertTrue(obj.pk)
        self.assertGreater(obj.version, original_version)

        form = formClass(self._get_form_data(version=obj.version), instance=obj)
        self.assertTrue(form.is_valid(), form.errors)
        pre_save_version = obj.version
        obj_after = form.save()

        self.assertTrue(obj_after.pk)
        self.assertGreater(obj_after.version, pre_save_version)


class ConcurrencyTest1(ConcurrencyTest0):
    def setUp(self):
        super(ConcurrencyTest1, self).setUp()
        self.TARGET = TestModel1(char_field="New", last_name="1")

    def test_force_update(self):
        from django.db import connection, transaction, DatabaseError, IntegrityError

        t = self.TARGET.__class__()
        self.assertRaises(DatabaseError, t.save, force_update=True)


class ConcurrencyTest2(ConcurrencyTest0):
    def setUp(self):
        super(ConcurrencyTest2, self).setUp()
        self.TARGET = TestModel2(char_field="New", last_name="1")

    def test_force_update(self):
        from django.db import connection, transaction, DatabaseError, IntegrityError

        t = self.TARGET.__class__()
        logger.debug("Object pk: %s version:%s", t.pk, t.version)
        self.assertRaises(DatabaseError, t.save, force_update=True)


class ConcurrencyTest3(ConcurrencyTest0):
    def setUp(self):
        super(ConcurrencyTest3, self).setUp()
        p, isnew = TestModel2.objects.get_or_create(char_field="New", last_name=str(time.time()))
        self.TARGET = TestModel3(char_field="New", last_name="1", fk=p)

    def test_force_update(self):
        from django.db import connection, transaction, DatabaseError, IntegrityError

        t = self.TARGET.__class__()
        self.assertRaises(DatabaseError, t.save, force_update=True)

    def test_concurrency(self):
        a = self.TARGET
        self._check_save(a)
        id = a.pk

        a = self.TARGET.__class__.objects.get(pk=id)
        v = a.version
        logger.debug("reloaded...now version is %s " % a.version)

        b = self.TARGET.__class__.objects.get(pk=id)
        assert a.version == b.version, "got same row with different version"
        time.sleep(1)
        a.last_name = "pippo"
        self._check_save(a)
        logger.debug("updated...now version is %s " % a.version)
        assert a.version > v, "same or lower version after update (%s,%s)" % (a.version, v)
        self.assertRaises(RecordModifiedError, b.save)


class ConcurrencyTest4(ConcurrencyTest0):
    def setUp(self):
        super(ConcurrencyTest4, self).setUp()
        self.TARGET = TestModel2(char_field="New", last_name="1")

    def test_manager(self):
        p1, isnew = TestModel2.objects.get_or_create(pk=1001, char_field="New", last_name="1")

        assert isnew is True
        p2, isnew = TestModel3.objects.get_or_create(pk=1002, char_field="New", last_name="1", fk=p1)
        assert isnew is True

        p1.save()
        p2.save()

#    def test_manager_2(self):
#        from django.db import connection, transaction, DatabaseError, IntegrityError
#        p, isnew = TestModel2.objects.get_or_create( pk = 1001, char_field = "New", last_name = "1" )
#
#        assert isnew is True
#        p, isnew = TestModel3.objects.get_or_create( pk = 1001, char_field = "New", last_name = "1", fk = p )
#        assert isnew is True


class ConcurrencyTest0_Proxy(ConcurrencyTest0):
    def setUp(self):
        super(ConcurrencyTest0_Proxy, self).setUp()
        self.TARGET = TestModel0_Proxy(char_field="New", last_name="1")

    def test_force_update(self):
        from django.db import connection, transaction, DatabaseError, IntegrityError

        t = self.TARGET.__class__()
        t.save(force_update=True)
        t1 = TestModel0.objects.get(pk=t.pk)
        self.assertEqual(t.pk, t1.pk)
        #self.assertRaises(ValueError,t.save,force_update=True )


class ConcurrencyTest2_Proxy(ConcurrencyTest2):
    def setUp(self):
        super(ConcurrencyTest2_Proxy, self).setUp()
        self.TARGET = TestModel2(char_field="New", last_name="1")


#class ConcurrencyTestUser(ConcurrencyTest0):
#    def setUp(self):
#        super(ConcurrencyTestUser, self).setUp()
#        self.TARGET = TestModelUser(username="New")
#
#    def test_form_save(self):
#        formClass = modelform_factory(self.TARGET.__class__)
#
#        data = dict(username="username", password='123',
#            date_joined=datetime.datetime.today(),
#            last_login=datetime.datetime.today())
#
#        form = formClass(data)
#
#        self.assertTrue(form.is_valid(), form.errors)
#        obj = form.save()
#        self.assertTrue(obj.pk)
#        v = obj.version
#        self.assertGreater(v, 0)
#
#        data['username'] = 'user'
#        data['version'] = v
#        form = formClass(data, instance=obj)
#        self.assertTrue(form.is_valid(), form.errors)
#        obj_after = form.save()
#        self.assertTrue(obj_after.pk)
#        self.assertGreater(obj_after.version, v)


class ConcurrencyTest5(ConcurrencyTest0):
    def setUp(self):
        super(ConcurrencyTest5, self).setUp()
        self.TARGET = TestAbstractModel0(char_field="New", last_name="1")


class ConcurrencyTestModelUser(ConcurrencyTest0):
    def setUp(self):
        super(ConcurrencyTestModelUser, self).setUp()
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


class ConcurrencyTestExistingModel(ConcurrencyTest0):
    """

    """
    version = IntegerVersionField()
    version.contribute_to_class(TestModelGroup, 'version')

    def setUp(self):
        super(ConcurrencyTestExistingModel, self).setUp()
        self._unique_field_name = 'name'
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
    def setUp(self):
        super(ConcurrencyTestModelWithCustomSave, self).setUp()
        self.TARGET = TestModelWithCustomSave(username="xxx", last_name="1")

    def _check_save(self, obj):
        self.assertEqual(obj.save(), 2222)


class ConcurrencyTestExistingModelWithCustomSave(ConcurrencyTest0):
    version = IntegerVersionField()
    version.contribute_to_class(TestModelGroupWithCustomSave, 'version')

    def setUp(self):
        super(ConcurrencyTestExistingModelWithCustomSave, self).setUp()
        self._unique_field_name = 'name'
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
