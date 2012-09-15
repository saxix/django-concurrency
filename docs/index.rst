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

How it works
============

|concurrency| works using a version field added to each model, each time a record is saved
the version number change (the algorithm used depeneds on the VersionField used, see :ref:`api`).

When a record is saved, |concurrency| try to get a lock to to the record based on the old revision
number, if the record is not found raise a :ref:`RecordModifiedError`

Application related models
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

`your_app.models.py`::

    from django.contrib.auth import User

    # add a version field to auth.User model
    version = IntegerVersionField()
    version.contribute_to_class(User, 'version')




Table Of Contents
=================

.. toctree::
    :maxdepth: 1

    help
    api

.. toctree::
    :hidden:

    globals

Links
=====

   * Project home page: https://github.com/saxix/django-concurrency
   * Issue tracker: https://github.com/saxix/django-concurrency/issues?sort
   * Download: http://pypi.python.org/pypi/django-concurrency/
   * Docs: http://readthedocs.org/docs/django-concurrency/en/latest/


