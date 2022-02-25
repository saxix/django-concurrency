from demo.models import SimpleConcurrentModel
from django.contrib import admin
from django.urls import re_path
from django.views.generic.edit import UpdateView

admin.autodiscover()

urlpatterns = (re_path(r'cm/(?P<pk>\d+)/',
                       UpdateView.as_view(model=SimpleConcurrentModel),
                       name='concurrent-edit'),
               re_path(r'^admin/', admin.site.urls))
