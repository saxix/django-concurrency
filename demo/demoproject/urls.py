from django.conf.urls import patterns, include
# from django.contrib.admin import ModelAdmin
from django.contrib import admin
from django.contrib.auth.models import User, Group
# from demoproject.demoapp.admin import DemoModelAdmin, ImportExportDemoModelAdmin
# from demoapp.admin import DemoModelAdmin, ImportExportDemoModelAdmin
# from demoapp.models import DemoModel, proxy_factory
from django.db import IntegrityError


class PublicAdminSite(admin.AdminSite):
    def has_permission(self, request):
        request.user = User.objects.get_or_create(username='sax')[0]
        return True


# public_site = PublicAdminSite()
admin.autodiscover()
# public_site.register([User, Group])
#
# for e, v in admin.site._registry.items():
#     public_site._registry[e] = v

# public_site.register(DemoModel, DemoModelAdmin)
# public_site.register(proxy_factory("ImportExport"), ImportExportDemoModelAdmin)
# u = User.objects.get_or_create(username='sax')[0]
# u.is_superuser=True
# u.set_password('123')
# u.save()

urlpatterns = patterns('',
                       # (r'^admin/', include(include(public_site.urls))),
                       (r'', include(include(admin.site.urls))))
