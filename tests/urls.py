from django.conf.urls import patterns, include
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       (r'^admin/', include(include(admin.site.urls))),
                       (r'', include(include(admin.site.urls))))
