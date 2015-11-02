.. include:: globals.txt
.. _admin:

==================
Admin Integration
==================

.. contents::
   :local:


.. _list_editable:

Handle ``list_editable``
------------------------
.. versionadded:: 0.6

|concurrency| is able to handle conflicts in the admin's changelist view when
:attr:`ModelAdmin.list_editable` is enabled. To enable this feature simply extend your ModelAdmin from
:ref:`ConcurrentModelAdmin` or use :ref:`ConcurrencyListEditableMixin`

.. seealso:: :ref:`list_editable_policies`


.. _admin_action:

Check admin's action execution for concurrency
----------------------------------------------

.. versionadded:: 0.6

Extend your ModelAdmin with :ref:`ConcurrencyActionMixin` or use :ref:`ConcurrentModelAdmin`



Update existing actions templates to be managed by concurrency
--------------------------------------------------------------

.. versionadded:: 0.6

You ca use the  :tfilter:`identity` filter to pass both ``pk`` and ``version`` to your ModelAdmin.
Each time you use ``{{ obj.pk }}`` simply change to ``{{ obj|identity }}``.
So in the ``admin/delete_selected_confirmation.html`` will have:

.. code-block:: html

    {% for obj in queryset %}
    <input type="hidden" name="{{ action_checkbox_name }}" value="{{ obj|identity }}" />
    {% endfor %}
