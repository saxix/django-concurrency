from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from concurrency.fields import IntegerVersionField

class AbstractConcurrentModel(models.Model):
    version = IntegerVersionField(db_column='cm_version_id')

    class Meta:
        abstract = True


class TestAbstractModel0(AbstractConcurrentModel):
    username = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    char_field = models.CharField(max_length=30, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True)


class ConcurrentModel(models.Model):
#    version = DateTimeVersionField( db_column = 'cm_version_id' )
    version = IntegerVersionField(db_column='cm_version_id')


class TestModel0(ConcurrentModel):
    username = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    char_field = models.CharField(max_length=30, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True)


class TestModel1(TestModel0):
    name1 = models.CharField(max_length=30, blank=True, null=True)


class TestModel2(TestModel1):
    name2 = models.CharField(max_length=30, blank=True, null=True)


class TestModel3(TestModel2):
    """ necessario per testare il comportamento diverso in caso di 'order_with_respect_to' """
    name3 = models.CharField(max_length=30, blank=True, null=True)
    fk = models.ForeignKey(TestModel2, related_name="parent", blank=True, null=True)

    class Meta:
        order_with_respect_to = 'fk'
        ordering = 'date_field'


class TestModel0_Proxy(TestModel0):
    class Meta:
        proxy = True


class TestModel2_Proxy(TestModel2):
    class Meta:
        proxy = True


class TestModelUser(User):
    version = IntegerVersionField(db_column='cm_version_id')
