from django.db import models
from concurrency import fields


class DemoModel(models.Model):
    version = fields.IntegerVersionField()
    char = models.CharField(max_length=255)
    integer = models.IntegerField()

    class Meta:
        app_label = 'demoapp'
