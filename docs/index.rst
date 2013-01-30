.. include:: globals.rst
.. _index:

==================
Django Concurrency
==================

Overview
========

.. image:: https://secure.travis-ci.org/saxix/django-concurrency.png?branch=master
   :target: http://travis-ci.org/saxix/django-concurrency/


django-concurrency is a optimistic locking library for Django Models

.. note:: |concurrency| requires Django >= 1.4


* easy to add to existing Models ( just add VersionField )
* works with Django internal models
* works with external models
* minimum intervention with existing database
* handle http post and standard python code (ie. django management commands)
* complete test suite (:ref:`test_suite`)
* works with `South`_ and `diango-reversion`_
* Admin integration

Table Of Contents
=================

.. toctree::
    :maxdepth: 1

    help
    api
    changes


.. toctree::
    :hidden:

    globals

How it works
============

|concurrency| works using a version field added to each model, each time a record is saved
the version number change (the algorithm used depeneds on the VersionField used, see :ref:`api`).

When a record is saved, |concurrency| try to get a lock to to the record based on the old revision
number, if the record is not found raise a :ref:`RecordModifiedError`

Add version to new models
--------------------------

`models.py`::

    from concurrency.fields import IntegerVersionField

    class ConcurrentModel( models.Model ):
        version = IntegerVersionField( )

`tests.py`::

    a = ConcurrentModel.objects.get(pk=1)
    b = ConcurrentModel.objects.get(pk=1)
    a.save()
    b.save() # this will raise ``RecordModifedError``


Django and/or plugged in applications models
--------------------------------------------

.. versionchanged:: 0.4

Concurrency can work even with existing models, anyway if you are adding concurrency management to
and existing database remember to edit the database's table:

`your_app.models.py`::

    from django.contrib.auth import User
    from concurrency.core import apply_concurrency_check

    apply_concurrency_check(User, 'version', IntegerVersionField)



Manually handle concurrency
---------------------------

.. versionchanged:: 0.4

::

    from concurrency.core import concurrency_check


    class AbstractModelWithCustomSave(models.Model):
        version = IntegerVersionField(db_column='cm_version_id', manually=True)


    def save(self, *args, **kwargs):
        concurrency_check(self, *args, **kwargs)
        logger.debug(u'Saving %s "%s".' % (self._meta.verbose_name, self))
        super(SecurityConcurrencyBaseModel, self).save(*args, **kwargs)


Test Utilities
--------------

:ref:`ConcurrencyTestMixin` offer a very simple test function for your existing models::

    from concurrency.utils import ConcurrencyTestMixin
    from myproject.models import MyModel

    class MyModelTest(ConcurrencyTestMixin, TestCase):
        concurrency_model = TestModel0
        concurrency_kwargs = {'username': 'test'}





Links
=====

   * Project home page: https://github.com/saxix/django-concurrency
   * Issue tracker: https://github.com/saxix/django-concurrency/issues?sort
   * Download: http://pypi.python.org/pypi/django-concurrency/
   * Docs: http://readthedocs.org/docs/django-concurrency/en/latest/


