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


If used with Django>=1.7 remember to create a custom migration.



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

Recovering deleted records with `diango-reversion`_ produces a
``RecordModifiedError``, because both `pk` and `version` are present in the
object, and |concurrency| tries to load the record (that does not exist),
which raises ``RecordModifiedError`` then.

To avoid this simply disable concurrency, by using a mixin:

.. code-block:: python

    class ConcurrencyVersionAdmin(reversion.admin.VersionAdmin):
    
        @disable_concurrency()
        def revision_view(self, request, object_id, version_id, extra_context=None):
            return super(ConcurrencyVersionAdmin, self).revision_view(
                request, object_id, version_id, extra_context=None)

        @disable_concurrency()
        def recover_view(self, request, version_id, extra_context=None):
            return super(ConcurrencyVersionAdmin, self).recover_view(
                request, version_id, extra_context)
