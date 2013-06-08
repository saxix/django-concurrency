from django.conf.urls import patterns, include, url
from django.contrib.admin import site
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Permission
from concurrency.admin import ConcurrentModelAdmin
from concurrency.tests.models import TestModel0, TestModel2, TestModel3, TestModel0_Proxy


if not TestModel0 in site._registry:
    site.register(TestModel0)

for m in [TestModel2, TestModel3, TestModel0_Proxy, Permission]:
    try:
        site.unregister(m)
    except NotRegistered:
        pass
        site.register(m, ConcurrentModelAdmin)

urlpatterns = patterns('', url(r'^admin/', include(site.urls)))
