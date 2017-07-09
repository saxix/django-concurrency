from django.conf.urls import url
from django.contrib import admin
from django.views.generic.edit import UpdateView

from demo.models import SimpleConcurrentModel

# try:
# from django.apps import AppConfig  # noqa
#     import django
#     django.setup()
# except ImportError:
#     pass

admin.autodiscover()

urlpatterns = (url('cm/(?P<pk>\d+)/',
                   UpdateView.as_view(model=SimpleConcurrentModel),
                   name='concurrent-edit'),
               url(r'^admin/',
                   admin.site.urls)
               )
