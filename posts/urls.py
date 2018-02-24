from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.list_posts),
    url(r'^(?P<id>[0-9]*)/?$', views.list_posts),
    url(r'^subj/?$', views.list_subjects),
    url(r'^subj/(?P<id_subj>[0-9]*)/?$', views.list_posts),
    url(r'^subjcp/?$', views.copy_subj),
    url(r'^add/?$', views.add_post),
    url(r'^edit/(?P<id>[0-9]*)/?$', views.edit_post),
    url(r'^del/(?P<id>[0-9]*)/?$', views.delete_post),
    url(r'^user/(?P<id>[0-9]*)/?$', views.user_profile),
]
