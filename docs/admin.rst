.. include:: globals.rst
.. _admin:

==================
Admin Integration
==================

.. contents::
   :local:


.. _list_editable:

Handle ``list_editable``
------------------------

Check admin's action execution for concurrency
----------------------------------------------

.. versionadded:: 0.6

Extend your ModelAdmin with `ConcurrencyActionMixin` or use `ConcurrentModelAdmin`


Update existing actions templates to be managed by concurrency
---------------------------------------------------------------

.. versionadded:: 0.6

You ca use the ``identity`` filter to pass both ``pk`` and ``version`` to your ModelAdmin.
Each time you use ``{{obj.pk}}`` simply change to ``{{ obj|identity }}``.
So in the ``admin/delete_selected_confirmation.html`` will have::

    {% for obj in queryset %}
    <input type="hidden" name="{{ action_checkbox_name }}" value="{{ obj|identity }}" />
    {% endfor %}

