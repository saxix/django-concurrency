# -*- coding: utf-8 -*-
'''
Created on 09/giu/2009

@author: sax
'''
import logging
import datetime
from django.db.utils import DatabaseError
from django.forms.models import modelform_factory
from django.utils.unittest.case import TestCase
from concurrency.models import RecordModifiedError
from django.db import transaction, models, connection
import time
from demoapp.models import *


logger = logging.getLogger('tests.concurrency')

class ConcurrencyError(Exception):
    pass


class ConcurrencyTest0(TestCase):
    def setUp( self ):
        super(ConcurrencyTest0, self).setUp()

        transaction.enter_transaction_management()
        transaction.managed(True)
        connection.close()

        self.TARGET = TestModel0(username="New", last_name="1")


    def tearDown( self ):
        super(ConcurrencyTest0, self).tearDown()
        transaction.rollback()
        transaction.leave_transaction_management()

    def test_standard_insert( self ):
        logger.debug("Created Object_1")
        a = self.TARGET.__class__(username='standard_insert')
        v = a.version
        logger.debug("Now Object_1.version is %s " % v)
        assert bool(v) == False, "version is not null %s" % v
        a.save()
        logger.debug("Object_1 saved...now version is %s " % a.version)
        self.assertTrue(a.pk > 0)
        assert a.version != v, "same or lower version after insert (%s,%s)" % ( a.version, v )
        b = self.TARGET.__class__.objects.get(pk=a.pk)
        self.assertEqual(a.version, b.version)

    def test_concurrency( self ):
        logger.debug("Created Object_1")
        a = self.TARGET
        a.save()
        logger.debug("Object_1 saved...now version is %s " % a.version)
        id = a.pk

        a = self.TARGET.__class__.objects.get(pk=id)
        v = a.version
        logger.debug("reloaded...now version is %s " % a.version)

        b = self.TARGET.__class__.objects.get(pk=id)
        assert a.version == b.version, "got same row with different version"
        time.sleep(2)
        a.last_name = "pippo"
        a.save()
        logger.debug("updated...now version is %s " % a.version)
        assert a.version != v, "same or lower version after update (%s,%s)" % ( a.version, v )
        self.assertRaises(RecordModifiedError, b.save)

    def test_concurrency_no_values( self ):
        logger.debug("Created Object_1")
        t = self.TARGET.__class__()
        assert bool(t.version) == False, "version is not null %s" % t.version
        t.save()
        self.assertTrue(t.pk > 0)
        self.assertTrue(t.version)

    def test_force_update( self ):
        logger.debug("Created Object_1")
        t = self.TARGET.__class__()
        self.assertRaises(DatabaseError, t.save, force_update=True)

    def test_force_insert( self ):
        logger.debug("Created Object_1")
        t = self.TARGET.__class__(username='empty')
        assert bool(t.version) == False, "version is not null %s" % t.version
        t.save(force_insert=True)
        self.assertTrue(t.pk > 0)
        self.assertTrue(t.version)

    def test_concurrency_manager_list( self ):
        logger.debug("Start Test")
        # test di concorrenza con list(queryset)
        for i in xrange(10, 13):
            #time.sleep(0.5)
            self.TARGET.__class__.objects.get_or_create(username="model %s" % i)
            # transaction.commit()

        prima_serie = list(self.TARGET.__class__.objects.all())
        seconda_serie = list(self.TARGET.__class__.objects.all())

        for el in prima_serie:
            el.last_name = "model %s 2^" % el.pk
            el.save()

        for el in seconda_serie:
            el.last_name = "model %s 3^" % el.pk
            self.assertRaises(RecordModifiedError, el.save)

    def test_concurrency_manager_get_item( self ):
        """ test di concorrenza con list(queryset) """
        logger.debug("Start Test")
        for i in xrange(3):
            #time.sleep(0.5)
            self.TARGET.__class__.objects.get_or_create(username="model %s" % i)

        prima_serie = self.TARGET.__class__.objects.all()
        seconda_serie = self.TARGET.__class__.objects.all()

        a = prima_serie[1]
        b = seconda_serie[1]
        a.last_name = "model %s 2^" % a.pk
        a.save()

        b.last_name = "model %s 3^" % b.pk
        self.assertRaises(RecordModifiedError, b.save)

    def test_form_save(self):
        formClass = modelform_factory(self.TARGET.__class__)
        form = formClass({}, instance=self.TARGET)

        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertTrue(obj.pk)
        v = obj.version
        self.assertEqual(v, 1)

        form = formClass({}, instance=obj)
        obj_after = form.save()
        self.assertTrue(obj_after.pk)
        self.assertEqual(obj_after.version, v + 1)


class ConcurrencyTest1(ConcurrencyTest0):
    def setUp( self ):
        super(ConcurrencyTest1, self).setUp()
        self.TARGET = TestModel1(char_field="New", last_name="1")

    def test_force_update( self ):
        from django.db import connection, transaction, DatabaseError, IntegrityError

        t = self.TARGET.__class__()
        self.assertRaises(DatabaseError, t.save, force_update=True)


class ConcurrencyTest2(ConcurrencyTest0):
    def setUp( self ):
        super(ConcurrencyTest2, self).setUp()
        self.TARGET = TestModel2(char_field="New", last_name="1")

    def test_force_update( self ):
        from django.db import connection, transaction, DatabaseError, IntegrityError

        t = self.TARGET.__class__()
        logger.debug("Object pk: %s version:%s", t.pk, t.version)
        self.assertRaises(DatabaseError, t.save, force_update=True)


class ConcurrencyTest3(ConcurrencyTest0):
    def setUp( self ):
        super(ConcurrencyTest3, self).setUp()
        p, isnew = TestModel2.objects.get_or_create(char_field="New", last_name=str(time.time()))
        self.TARGET = TestModel3(char_field="New", last_name="1", fk=p)

    def test_force_update( self ):
        from django.db import connection, transaction, DatabaseError, IntegrityError

        t = self.TARGET.__class__()
        self.assertRaises(DatabaseError, t.save, force_update=True)

    def test_concurrency( self ):
        a = self.TARGET
        a.save()
        id = a.pk

        a = self.TARGET.__class__.objects.get(pk=id)
        v = a.version
        logger.debug("reloaded...now version is %s " % a.version)

        b = self.TARGET.__class__.objects.get(pk=id)
        assert a.version == b.version, "got same row with different version"
        time.sleep(1)
        a.last_name = "pippo"
        a.save()
        logger.debug("updated...now version is %s " % a.version)
        assert a.version > v, "same or lower version after update (%s,%s)" % ( a.version, v )
        self.assertRaises(RecordModifiedError, b.save)


class ConcurrencyTest4(ConcurrencyTest0):
    def setUp( self ):
        super(ConcurrencyTest4, self).setUp()
        self.TARGET = TestModel2(char_field="New", last_name="1")

    def test_manager( self ):
        from django.db import connection, transaction, DatabaseError, IntegrityError

        p, isnew = TestModel2.objects.get_or_create(pk=1001, char_field="New", last_name="1")

        assert isnew == True
        p, isnew = TestModel3.objects.get_or_create(pk=1002, char_field="New", last_name="1", fk=p)
        assert isnew == True

#    def test_manager_2( self ):
#        from django.db import connection, transaction, DatabaseError, IntegrityError
#        p, isnew = TestModel2.objects.get_or_create( pk = 1001, char_field = "New", last_name = "1" )
#
#        assert isnew == True
#        p, isnew = TestModel3.objects.get_or_create( pk = 1001, char_field = "New", last_name = "1", fk = p )
#        assert isnew == True

class ConcurrencyTest0_Proxy(ConcurrencyTest0):
    def setUp( self ):
        super(ConcurrencyTest0_Proxy, self).setUp()
        self.TARGET = TestModel0_Proxy(char_field="New", last_name="1")

    def test_force_update( self ):
        from django.db import connection, transaction, DatabaseError, IntegrityError

        t = self.TARGET.__class__()
        t.save(force_update=True)
        t1 = TestModel0.objects.get(pk=t.pk)
        self.assertEqual(t.pk, t1.pk)
        #self.assertRaises(ValueError,t.save,force_update=True )


class ConcurrencyTest2_Proxy(ConcurrencyTest2):
    def setUp( self ):
        super(ConcurrencyTest2_Proxy, self).setUp()
        self.TARGET = TestModel2(char_field="New", last_name="1")


class ConcurrencyTestUser(ConcurrencyTest0):
    def setUp( self ):
        super(ConcurrencyTestUser, self).setUp()
        self.TARGET = TestModelUser(username="New")

    def test_form_save(self):
#        TARGET = TestModelUser(username="New", password='123', date_joined=datetime.datetime.today(),
#            last_login=datetime.datetime.today())
        formClass = modelform_factory(self.TARGET.__class__)
        data = dict(username="username", password='123', date_joined=datetime.datetime.today(),
            last_login=datetime.datetime.today())
        form = formClass(data)

        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertTrue(obj.pk)
        v = obj.version
        self.assertEqual(v, 1)

        data['username'] = 'user'
        form = formClass(data, instance=obj)
        self.assertTrue(form.is_valid(), form.errors)
        obj_after = form.save()
        self.assertTrue(obj_after.pk)
        self.assertEqual(obj_after.version, v + 1)


class ConcurrencyTest5(ConcurrencyTest0):
    def setUp( self ):
        super(ConcurrencyTest5, self).setUp()
        self.TARGET = TestAbstractModel0(char_field="New", last_name="1")


