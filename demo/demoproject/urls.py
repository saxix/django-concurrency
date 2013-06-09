from django.conf.urls import patterns, include, url
from django.contrib.admin import ModelAdmin
import django.contrib.admin.sites
from django.contrib import admin
from django.contrib.admin.sites import site
from django.contrib.auth.models import User, Permission, Group
from demoproject.demoapp.admin import DemoModelAdmin
from demoproject.demoapp.models import DemoModel

admin.autodiscover()


class PublicAdminSite(django.contrib.admin.sites.AdminSite):
    def has_permission(self, request):
        request.user = User.objects.get_or_create(username='sax')[0]
        return True

public_site = PublicAdminSite()
django.contrib.admin.autodiscover()
public_site.register([User, Group])
public_site.register(DemoModel, DemoModelAdmin)

urlpatterns = patterns('',
                       (r'^admin/', include(include(public_site.urls))),
                       (r'', include(include(public_site.urls))),
                       )
