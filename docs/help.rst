.. include:: globals.rst

.. _help:

Installation
------------

Using ``pip``::

    pip install django-concurrency

Go to https://github.com/saxix/django-concurrency if you need to download a package or clone the repo.


Setup
-----
|concurrency| does not need to be installed into ``INSTALLED_APPS`` unless you want run tests


.. _test_suite:

Test suite
----------

|concurrency| come with a set of tests that can simulate different scenarions

* basic versioned model
* inherited model
* inherited model from abstract model
* inherited model from external projcet model
* django User model
* models with custom save

