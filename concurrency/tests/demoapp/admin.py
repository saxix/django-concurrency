from django.contrib.admin import site
from concurrency.tests.demoapp.models import TestModel0, TestModel1, TestModel2, TestModel3, TestModel0_Proxy


site.register(TestModel0)
site.register(TestModel1)
site.register(TestModel2)
site.register(TestModel3)
site.register(TestModel0_Proxy)
