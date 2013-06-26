.. include:: globals.rst
.. _index:

==================
Django Concurrency
==================

Overview
========

.. image:: https://secure.travis-ci.org/saxix/django-concurrency.png?branch=master
   :target: http://travis-ci.org/saxix/django-concurrency/


django-concurrency is an optimistic locking library for Django Models

It prevents users from doing concurrent editing in Django both from UI and from a
django command.


.. note:: |concurrency| requires Django >= 1.4


* easy to add to existing Models ( just add VersionField )
* works with Django internal models
* works with third-party models
* minimum intervention with existing database
* handle http post and standard python code (ie. django management commands)
* complete test suite (:ref:`test_suite`)
* works with `South`_ and `diango-reversion`_
* Admin integration (handle :ref:`actions <admin_action>` and :ref:`list_editable <list_editable>`)


Todo
====

- intercept external updates
    (ie changes done using DB browser like SQLDeveloper, pgAdmin, phpMyAdmin...)
-

How it works
============

|concurrency| works using a version field added to each model, each time a record is saved
the version number changes (the algorithm used depends on the VersionField used,
(see :ref:`fields`).

When a record is saved, |concurrency| tries to get a lock on the record based on the old revision
number, if the record is not found a :ref:`RecordModifiedError` is raised


Table Of Contents
=================

.. toctree::
    :maxdepth: 1

    install
    fields
    middleware
    admin
    api
    settings
    cookbook
    changes


Links
=====

   * Project home page: https://github.com/saxix/django-concurrency
   * Issue tracker: https://github.com/saxix/django-concurrency/issues?sort
   * Download: http://pypi.python.org/pypi/django-concurrency/
   * Docs: http://readthedocs.org/docs/django-concurrency/en/latest/


