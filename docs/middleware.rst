.. include:: globals.rst

.. _middleware:

ConcurrencyMiddleware
=====================

You can globally intercept :ref:`RecordModifiedError`
adding :ref:`concurrency.middleware.ConcurrencyMiddleware <concurrencymiddleware>` to your :setting:`MIDDLEWARE_CLASSES`.
Each time a ``RecordModifiedError`` is raised a go up to the ConcurrencyMiddleware the handler defined in
:setting:`CONCURRECY_HANDLER409` is invoked.



