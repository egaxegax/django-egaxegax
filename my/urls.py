from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.list_photos),
    url(r'^album/(?P<id_album>[0-9]*)/?$', views.list_photos),
    url(r'^(?P<id>[0-9]*)/(?P<size>[0-9]*)/?$', views.get_photo),
    url(r'^orig/(?P<id>[0-9]*)/?$', views.get_photo_orig),
    url(r'^orig/(?P<id>[0-9]*)/(?P<size>[0-9]*)/?$', views.get_photo_orig),
    url(r'^add/?$', views.add_photo),
    url(r'^edit/(?P<id>[0-9]*)/?$', views.edit_photo),
    url(r'^del/(?P<id>[0-9]*)/?$', views.delete_photo),
    url(r'^(?P<part>[^/]*)/(?P<titl>[^/]*)/?$', views.get_thumb),
]
