from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.list_msg),
    url(r'^(?P<all>all)/?$', views.list_msg),
    url(r'^add/?$', views.add_msg),
    url(r'^edit/(?P<id>[0-9]*)/?$', views.edit_msg),
    url(r'^del/(?P<id>[0-9]*)/?$', views.delete_msg),
    url(r'^user/(?P<id>[0-9]*)/?$', views.user_profile),
]
