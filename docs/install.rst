.. include:: globals.rst

.. _help:

Install
=======

Using ``pip``::

    pip install django-concurrency

Go to https://github.com/saxix/django-concurrency if you need to download a package or clone the repo.


|concurrency| does not need to be installed into ``INSTALLED_APPS`` unless you want run tests



.. _test_suite:

----------
Test suite
----------

|concurrency| come with a set of tests that can simulate different scenarions

* basic versioned model
* inherited model
* inherited model from abstract model
* inherited model from external projcet model
* django User model
* models with custom save

How to run the tests
---------------------

Option 1: using tox
~~~~~~~~~~~~~~~~~~~
    ::

        $ pip install tox
        $ tox

Option 2: using demo project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ::

        $ cd demo
        $ ./manage.py test adminactions

Option 3: execute in your project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    simply add concurrency in your :setting:`INSTALLED_APPS`
    ::

        INSTALLED_APPS = (
            'concurrency',
            ...
        )

