.. include:: globals.txt
.. _index:

==================
Django Concurrency
==================

Overview
========

.. image:: https://img.shields.io/travis/saxix/django-concurrency/master.svg
    :target: http://travis-ci.org/saxix/django-concurrency/
    :alt: Test status

.. image:: https://codecov.io/github/saxix/django-concurrency/coverage.svg?branch=master
    :target: https://codecov.io/github/saxix/django-concurrency?branch=master
    :alt: Coverage



django-concurrency is an optimistic locking library for Django Models

It prevents users from doing concurrent editing in Django both from UI and from a
django command.



* easy to add to existing Models (just add :ref:`concurrency.fields.VersionField` )
* can be added with Django internal models (ie `auth.User` or `auth.Group`)
* handle http post and standard python code (ie. django management commands)
* complete test suite (:ref:`test_suite`)
* Admin integration. Handle :ref:`actions <admin_action>` and :ref:`list_editable <list_editable>` (solves :django_issue:`11313`)
* can handle external updates (see :ref:`concurrency.fields.TriggerVersionField`)

How it works
============


Overview
--------

|concurrency| works adding a :class:`concurrency.fields.VersionField` to each model,
each time a record is saved the version number changes (the algorithm used depends
on the implementation of :class:`concurrency.fields.VersionField` used (see :ref:`fields`).


Each update is converted in the following SQL clause like:

.. code-block:: sql

    UPDATE mymodel SET version=NEW_VERSION, ... WHERE id = PK AND version = VERSION_NUMBER


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
    faq


Links
=====

   * Project home page: https://github.com/saxix/django-concurrency
   * Issue tracker: https://github.com/saxix/django-concurrency/issues?sort
   * Download: http://pypi.python.org/pypi/django-concurrency/
   * Docs: http://readthedocs.org/docs/django-concurrency/en/latest/



.. [1] http://en.wikipedia.org/wiki/Optimistic_concurrency_control
