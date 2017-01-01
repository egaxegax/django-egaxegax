from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.upload_handler),
    url(r'(?P<pk>\d+)', views.download_handler),
]