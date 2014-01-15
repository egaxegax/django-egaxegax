from django.conf.urls.defaults import *

urlpatterns = patterns('mynews.views',
    (r'^$', 'list_msg'),
    (r'^(?P<all>all)/?$', 'list_msg'),
    (r'^add/?$', 'add_msg'),
    (r'^edit/(?P<id>[0-9]*)/?$', 'edit_msg'),
    (r'^del/(?P<id>[0-9]*)/?$', 'delete_msg'),
    (r'^user/(?P<id>[0-9]*)/?$', 'get_user_profile'),
)
