from django.core.checks import Warning, register, Error
from django.db import router, connections

from concurrency.triggers import factory


@register(deploy=True)
def trigger_esists(app_configs, **kwargs):
    global _TRIGGERS
    from concurrency.fields import _TRIGGERS
    errors = []
    for field in _TRIGGERS:
        model = field.model
        alias = router.db_for_write(model)
        connection = connections[alias]
        f = factory(connection)
        if not f.get_trigger(field):
            errors.append(
                Error(
                    'Missed trigger for field {}'.format(field),
                    hint=None,
                    obj=None,
                    id='concurrency.W001',
                )
            )
    return errors
