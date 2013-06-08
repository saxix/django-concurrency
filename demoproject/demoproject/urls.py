from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.admin.sites import site

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(site.urls)),
                       )
