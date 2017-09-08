from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.list_photos),
    url(r'^album/(?P<id_album>[0-9]*)/?$', views.list_photos),
    url(r'^orig/?$', views.get_photo),
    url(r'^orig/(?P<id>[0-9]*)/?$', views.get_photo),
    url(r'^view/(?P<id>[0-9]*)/?$', views.view_photo),
    url(r'^add/?$', views.add_photo),
    url(r'^edit/(?P<id>[0-9]*)/?$', views.edit_photo),
    url(r'^del/(?P<id>[0-9]*)/?$', views.delete_photo),
]
