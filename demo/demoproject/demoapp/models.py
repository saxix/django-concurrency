from django.db import models
from concurrency import fields


class DemoModel(models.Model):
    version = fields.IntegerVersionField()
    char = models.CharField(max_length=255)
    integer = models.IntegerField()

    class Meta:
        app_label = 'demoapp'


class ProxyDemoModel(DemoModel):
    class Meta:
        app_label = 'demoapp'
        proxy = True


def proxy_factory(name):
    return type(name, (ProxyDemoModel,), {'__module__': ProxyDemoModel.__module__,
                                          'Meta': type('Meta', (object,), {'proxy': True, 'app_label': 'demoapp'})})
