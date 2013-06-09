from django.conf.urls import patterns, include, url
from django.contrib.admin import site

urlpatterns = patterns('', url(r'^admin/', include(site.urls)))
