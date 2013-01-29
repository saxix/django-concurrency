from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.base import ModelBase
from concurrency.core import concurrency_check
from concurrency.fields import IntegerVersionField
from concurrency.fields import RawIntegerVersionField
from concurrency.fields import AutoIncVersionField


class AbstractConcurrentModel(models.Model):
    version = IntegerVersionField(db_column='cm_version_id')

    class Meta:
        abstract = True
        app_label = 'concurrency'


class TestAbstractModel0(AbstractConcurrentModel):
    username = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    char_field = models.CharField(max_length=30, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'concurrency'


class ConcurrentModel(models.Model):
    version = IntegerVersionField(db_column='cm_version_id')

    class Meta:
        app_label = 'concurrency'

class ConcurrentAutoIncModel(models.Model):
    version = AutoIncVersionField(db_column='cm_version_id')

    class Meta:
        app_label = 'concurrency'

class MyMeta(ModelBase):
    pass

class AbstractModelWithCustomSave(models.Model):
    __metaclass__ = MyMeta
    version = RawIntegerVersionField(db_column='cm_version_id')

    class Meta:
        abstract = True
        app_label = 'concurrency'

    def save(self, force_insert=False, force_update=False, using=None):
        concurrency_check(self)
        super(AbstractModelWithCustomSave, self).save(force_insert, force_update, using)
        return 'AbstractModelWithCustomSave'

class ModelWithAbstractCustomSave(AbstractModelWithCustomSave):
    username = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        app_label = 'concurrency'

#    def save(self, force_insert=False, force_update=False, using=None):
#        super(ModelWithAbstractCustomSave, self).save(force_insert, force_update, using)
#        return 'ModelWithAbstractCustomSave'


class TestModel0(ConcurrentModel):
    username = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    char_field = models.CharField(max_length=30, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'concurrency'


class TestModel1(TestModel0):
    name1 = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        app_label = 'concurrency'


class TestModel2(TestModel1):
    name2 = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        app_label = 'concurrency'


class TestModel3(TestModel2):
    """ necessario per testare il comportamento diverso in caso di 'order_with_respect_to' """
    name3 = models.CharField(max_length=30, blank=True, null=True)
    fk = models.ForeignKey(TestModel2, related_name="parent", blank=True, null=True)

    class Meta:
        order_with_respect_to = 'fk'
        ordering = 'date_field'
        app_label = 'concurrency'


class TestModel0_Proxy(TestModel0):
    class Meta:
        proxy = True
        app_label = 'concurrency'


class TestModel2_Proxy(TestModel2):
    class Meta:
        proxy = True


class TestModelWithCustomSave(ConcurrentModel):
    username = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        app_label = 'concurrency'

    def save(self, force_insert=False, force_update=False, using=None):
        super(TestModelWithCustomSave, self).save(force_insert, force_update, using)
        return 2222


class TestModelUser(User):
    version = IntegerVersionField(db_column='cm_version_id')

    class Meta:
        app_label = 'concurrency'


class TestModelGroup(Group):
    #HACK: this field is here because all tests relies on that
    # and we need a 'fresh' model to check for on-the-fly addition
    # of version field.  (added in concurrency 0.3.0)

    username = models.CharField('username', max_length=50)

    class Meta:
        app_label = 'concurrency'


class TestModelGroupWithCustomSave(TestModelGroup):

    class Meta:
        app_label = 'concurrency'

    def save(self, force_insert=False, force_update=False, using=None):
        super(TestModelGroupWithCustomSave, self).save(force_insert, force_update, using)
        return 2222 # dummy return only for tests


class TestIssue3Model(models.Model):
    username = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    char_field = models.CharField(max_length=30, blank=True, null=True)
    date_field = models.DateField(blank=True, null=True)

    version = models.CharField(default='abc', max_length=10, blank=True, null=True)
    revision = IntegerVersionField(db_column='cm_version_id')

    class Meta:
        app_label = 'concurrency'

