.. include:: globals.rst
.. _cookbook:

========
Cookbook
========

.. contents::
   :local:


Add version to new models
--------------------------

`models.py`::

    from concurrency.fields import IntegerVersionField

    class ConcurrentModel( models.Model ):
        version = IntegerVersionField( )

`tests.py`::

    a = ConcurrentModel.objects.get(pk=1)
    b = ConcurrentModel.objects.get(pk=1)
    a.save()
    b.save() # this will raise ``RecordModifedError``


Django and/or plugged in applications models
--------------------------------------------

.. versionchanged:: 0.4

Concurrency can work even with existing models, anyway if you are adding concurrency management to
and existing database remember to edit the database's table:

`your_app.models.py`::

    from django.contrib.auth import User
    from concurrency.api import apply_concurrency_check

    apply_concurrency_check(User, 'version', IntegerVersionField)



Manually handle concurrency
---------------------------

.. versionchanged:: 0.4

::

    from concurrency.api import concurrency_check


    class AbstractModelWithCustomSave(models.Model):
        version = IntegerVersionField(db_column='cm_version_id', manually=True)


    def save(self, *args, **kwargs):
        concurrency_check(self, *args, **kwargs)
        logger.debug(u'Saving %s "%s".' % (self._meta.verbose_name, self))
        super(SecurityConcurrencyBaseModel, self).save(*args, **kwargs)


Test Utilities
--------------

:ref:`ConcurrencyTestMixin` offer a very simple test function for your existing models::

    from concurrency.utils import ConcurrencyTestMixin
    from myproject.models import MyModel

    class MyModelTest(ConcurrencyTestMixin, TestCase):
        concurrency_model = TestModel0
        concurrency_kwargs = {'username': 'test'}

