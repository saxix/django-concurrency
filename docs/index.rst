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

.. image:: https://requires.io/github/saxix/django-concurrency/requirements.png?branch=master
    :target: https://requires.io/github/saxix/django-concurrency/requirements/?branch=master
    :alt: Requirements Status



    django-concurrency is an optimistic locking library for Django Models

    It prevents users from doing concurrent editing in Django both from UI and from a
    django command.


.. note:: |concurrency| requires Django >= 1.4


* easy to add to existing Models (just add :class:`concurrency.fields.VersionField` )
* works with third-party models (see :ref:`apply_concurrency_check`)
* works with Django internal models
* handle http post and standard python code (ie. django management commands)
* complete test suite (:ref:`test_suite`)
* works with `South`_ and `diango-reversion`_
* Admin integration. Handle :ref:`actions <admin_action>` and :ref:`list_editable <list_editable>` (solves :django_issue:`11313`)
* can handle external updates (see :class:`TriggerVersionField`)
Todo
====

- intercept external updates
    (ie changes done using DB browser like SQLDeveloper, pgAdmin, phpMyAdmin...)

.. _protocols:

How it works
============

|concurrency| works adding a :class:`concurrency.fields.VersionField` to each model, each time a record is saved
the version number changes (the algorithm used depends on the implementation of
:class:`concurrency.fields.VersionField` used (see :ref:`fields`).


|concurrency| use two different way to manage concurrent updates:

django 1.4 - 1.5
----------------

When a record is saved, |concurrency| tries to get a lock on the record based on the old revision
number, if the record is not found a :ref:`RecordModifiedError` is raised.
The lock is obtained using ``SELECT FOR UPDATE`` and it's requirend
to prevent other updates during the internal django ``save()`` execution.

django >= 1.6
-----------------

Full implementation of ``optimistic-lock`` pattern using a SQL clause like:

.. code-block:: sql

    UPDATE mymodel SET version=NEW_VERSION, ... WHERE id = PK AND version = VERSION_NUMBER


.. _2_protocols:

Why two protocols ?
-------------------
The initial implementation of |concurrency| used the real pattern [1],
but it required a partial rewrite of original Django's code and it was
very hard to maintain/keep updated, for this reason starting from version 0.3,
:ref:`select_for_update()` was used.

With the new  implementation (django 1.6) the optimistic lock pattern it
is easier to implement, starting from version 0.7 C uses different implementation
depending on the django version used.

.. note:: From 1.0 support for django < 1.6 will be drooped


.. seealso:: :setting:`USE_SELECT_FOR_UPDATE`

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



.. [1] http://en.wikipedia.org/wiki/Optimistic_concurrency_control

