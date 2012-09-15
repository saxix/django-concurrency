from django.conf.urls import patterns, include, url
from django.contrib.admin import site
from concurrency.tests.models import TestModel0, TestModel1, TestModel2, TestModel3, TestModel0_Proxy


if not TestModel0 in site._registry:
    site.register(TestModel0)

site.register(TestModel1)
site.register(TestModel2)
site.register(TestModel3)
site.register(TestModel0_Proxy)

urlpatterns = patterns('',
    url(r'^admin/', include(site.urls)),
)
