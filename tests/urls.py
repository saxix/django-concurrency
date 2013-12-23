from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.edit import UpdateView
from tests.models import SimpleConcurrentModel

admin.autodiscover()


class SimpleConcurrentMpdel(object):
    pass


urlpatterns = patterns('',
                       url('cm/(?P<pk>\d+)/',
                       UpdateView.as_view(model=SimpleConcurrentModel),
                       name='concurrent-edit'),
                       (r'^admin/', include(include(admin.site.urls))),
                       (r'', include(include(admin.site.urls))))
