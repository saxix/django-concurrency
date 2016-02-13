.. include:: globals.txt

.. _help:

Install
=======

Using ``pip``::

    pip install django-concurrency

Go to https://github.com/saxix/django-concurrency if you need to download a package or clone the repo.


|concurrency| does not need to be added into ``INSTALLED_APPS`
unless you want to run the tests or use the templatetags and/or admin integration


.. _test_suite:

----------
Test suite
----------

|concurrency| comes with a set of tests that can simulate different scenarios

* basic versioned model
* inherited model
* inherited model from abstract model
* inherited model from external project model
* django User model
* models with custom save
* proxy models
* admin actions


How to run the tests
--------------------

.. code-block:: bash

        $ pip install tox
        $ tox

