.. include:: globals.txt
.. _index:

==================
Django Concurrency
==================

Overview
========

.. image:: https://secure.travis-ci.org/saxix/django-concurrency.png?branch=master
    :target: http://travis-ci.org/saxix/django-concurrency/
    :alt: Test status

.. image:: https://coveralls.io/repos/saxix/django-concurrency/badge.png?branch=master
    :target: https://coveralls.io/r/saxix/django-concurrency
    :alt: Coverage

.. image:: https://pypip.in/v/django-concurrency/badge.png
    :target: https://crate.io/packages/django-concurrency/

.. image:: https://pypip.in/d/django-concurrency/badge.png
    :target: https://crate.io/packages/django-concurrency/
    :alt: Downloads




django-concurrency is an optimistic locking library for Django Models

It prevents users from doing concurrent editing in Django both from UI and from a
django command.



* easy to add to existing Models (just add :ref:`concurrency.fields.VersionField` )
* works with third-party models (see :ref:`apply_concurrency_check`)
* works with Django internal models
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

