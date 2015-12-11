.. include:: globals.txt
.. _cookbook:

========
Cookbook
========

.. contents::
   :local:



.. _import_data:

Unable to import data ?
-----------------------

Sometimes you need to temporary disable concurrency (ie during data imports)

**Temporary disable per Model**

.. code-block:: python

    from concurrency.api import disable_concurrency

    with disable_concurrency(instance):
        Model.object



Add version management to new models
------------------------------------

:file:`models.py`

.. code-block:: python

    from concurrency.fields import IntegerVersionField

    class ConcurrentModel( models.Model ):
        version = IntegerVersionField( )

:file:`tests.py`

.. code-block:: python

    a = ConcurrentModel.objects.get(pk=1)
    b = ConcurrentModel.objects.get(pk=1)
    a.save()
    b.save() # this will raise ``RecordModifiedError``


Add version management to Django and/or plugged in applications models
----------------------------------------------------------------------

.. versionchanged:: 0.8


Concurrency can work even with existing models, anyway if you are adding concurrency management to
an existing database remember to edit the database's tables:

:file:`your_app.models.py`

.. code-block:: python

    from django.contrib.auth import User
    from concurrency.api import apply_concurrency_check

    apply_concurrency_check(User, 'version', IntegerVersionField)


If used with Django>=1.7 remebber to create a custom migration.


Manually handle concurrency
---------------------------
.. versionchanged:: 0.4

Use :ref:`concurrency_check`


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


Recover deleted record with django-reversion
--------------------------------------------

Recovering delete record with `diango-reversion`_ produce a ``RecordModifeidError``.
As both pk and version are present in the object, |concurrency| try to load the record (that does not exists)
and this raises ``RecordModifedError``. To avoid this simply:

.. code-block:: python

    class ConcurrencyVersionAdmin(reversionlib.VersionAdmin):
        def render_revision_form(self, request, obj, version, context, revert=False, recover=False):
            with disable_concurrency(obj):
                return super(ConcurrencyVersionAdmin, self).render_revision_form(request, obj, version, context, revert, recover)


or for (depending on django-reversion version)

.. code-block:: python

    class ConcurrencyVersionAdmin(reversionlib.VersionAdmin):

       @disable_concurrency()
       def recover_view(self, request, version_id, extra_context=None):
            return super(ReversionConcurrentModelAdmin, self).recover_view(request,
                                                                version_id,
                                                                extra_context)
