.. include:: globals.rst
.. _cookbook:

========
Cookbook
========

.. contents::
   :local:

.. _import_data:

Unable to import data ?
-----------------------

|concurrency| check that any model, when saved, has no version, anyway this is not true
when you are importing data from a file or loading a fixture.
This is internally known as ``SANITY_CHECK``. To solve this you can:

**Globally disable:**

`settings.py`
.. code-block:: python

        CONCURRENCY_SANITY_CHECK = False

**Temporary disable**
.. code-block:: python

    from concurrency.config import conf

    conf.SANITY_CHECK = False

**Temporary disable per Model**
.. code-block:: python

    from concurrency.api import disable_sanity_check

    with disable_sanity_check(Model):
        Model.object



Add version management to new models
-------------------------------------

`models.py`
.. code-block:: python

    from concurrency.fields import IntegerVersionField

    class ConcurrentModel( models.Model ):
        version = IntegerVersionField( )

`tests.py`
.. code-block:: python

    a = ConcurrentModel.objects.get(pk=1)
    b = ConcurrentModel.objects.get(pk=1)
    a.save()
    b.save() # this will raise ``RecordModifiedError``


Add version management to Django and/or plugged in applications models
-----------------------------------------------------------------------

.. versionchanged:: 0.4

Concurrency can work even with existing models, anyway if you are adding concurrency management to
an existing database remember to edit the database's tables:

`your_app.models.py`
.. code-block:: python

    from django.contrib.auth import User
    from concurrency.api import apply_concurrency_check

    apply_concurrency_check(User, 'version', IntegerVersionField)



Manually handle concurrency
---------------------------
.. versionchanged:: 0.4

Use :function:`concurrency.api.concurrency_check`


.. code-block:: python

    from concurrency.api import concurrency_check


    class AbstractModelWithCustomSave(models.Model):
        version = IntegerVersionField(db_column='cm_version_id', manually=True)


    def save(self, *args, **kwargs):
        concurrency_check(self, *args, **kwargs)
        logger.debug(u'Saving %s "%s".' % (self._meta.verbose_name, self))
        super(SecurityConcurrencyBaseModel, self).save(*args, **kwargs)


Test Utilities
--------------

:ref:`ConcurrencyTestMixin` offer a very simple test function for your existing models

.. code-block:: python

    from concurrency.utils import ConcurrencyTestMixin
    from myproject.models import MyModel

    class MyModelTest(ConcurrencyTestMixin, TestCase):
        concurrency_model = TestModel0
        concurrency_kwargs = {'username': 'test'}

