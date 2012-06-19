.. |concurrency| replace:: Concurrency
.. |version| replace:: 0.1

.. _help:

Installation
------------

Using ``pip``::

    pip install django-concurrency

Go to https://github.com/saxix/django-concurrency if you need to download a package or clone the repo.


Setup
-----
|concurrency| does not need to be installed into ``INSTALLED_APPS`` unless you want run tests


Testing
-------

|concurrency| come with a set of test that can tests many scenarions

* basic versioned model
* inherited model
* inherited model from abstract model
* inherited model from external projcet model



Howto
-----

Just add a field of `IntegerVersionField` to your model::


    from concurrency.fields import IntegerVersionField

    class ConcurrentModel( models.Model ):
        version = IntegerVersionField( )



