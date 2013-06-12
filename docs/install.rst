.. include:: globals.rst

.. _help:

Install
=======

Using ``pip``::

    pip install django-concurrency

Go to https://github.com/saxix/django-concurrency if you need to download a package or clone the repo.


|concurrency| does not need to be installed into ``INSTALLED_APPS`` unless you want run tests

--------------------
Configure the Signer
--------------------

``VersionField`` is managed by by the Form using an ``HiddenInput`` widget, anyway to be sure that the version is not
tampered with, its value is `signed`. The default VersionSigner is ``concurrency.forms.VersionFieldSigner`` that simply
extends ``django.core.signing.Signer``. If you want change your Signer you can set ``CONCURRENCY_FIELD_SIGNER`` in your settings

    ``mysigner.py`` ::

        class DummySigner():
            """ Dummy signer that simply returns the raw version value. (Simply do not sign it) """
            def sign(self, value):
                return smart_str(value)

            def unsign(self, signed_value):
                return smart_str(signed_value)

    ``settings.py`` ::

        CONCURRENCY_FIELD_SIGNER = "myapp.mysigner.DummySigner"



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

How to run it
-------------

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

