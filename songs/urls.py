from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.list_songs),
    url(r'^(?P<id>[0-9]*)/?$', views.get_song),
    url(r'^(?P<id>[0-9]*)/(?P<title>[^/]*)?$', views.get_song),
    url(r'^artcp/?$', views.copy_art),
    url(r'^art/i/(?P<ind_art>[0-9]*)/?$', views.list_art),
    url(r'^art/?$', views.list_art),
    url(r'^art/(?P<id_art>[0-9]*)/?$', views.list_songs),
    url(r'^add/?$', views.add_song),
    url(r'^del/(?P<id>[0-9]*)/?$', views.delete_song),
    url(r'^edit/(?P<id>[0-9]*)/?$', views.edit_song),
    url(r'^user/(?P<id>[0-9]*)/?$', views.user_profile),
]
