.. |concurrency| replace:: Concurrency
.. |version| replace:: 0.1

.. _howto:

Howto
=====

Just add a field of `IntegerVersionField` to your model::


    from concurrency.fields import IntegerVersionField

    class ConcurrentModel( models.Model ):
        version = IntegerVersionField( )



