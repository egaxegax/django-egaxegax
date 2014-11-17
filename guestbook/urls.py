from django.conf.urls import *

urlpatterns = patterns('guestbook.views',
    (r'^$', 'list_posts'),
    (r'^(?P<id>[0-9]*)/?$', 'list_posts'),
    (r'^subj/?$', 'list_subjects'),
    (r'^subj/(?P<id_subj>[0-9]*)/?$', 'list_posts'),
    (r'^subjcp/?$', 'copy_subj'),
    (r'^add/?$', 'add_post'),
    (r'^edit/(?P<id>[0-9]*)/?$', 'edit_post'),
    (r'^del/(?P<id>[0-9]*)/?$', 'delete_post'),
    (r'^user/(?P<id>[0-9]*)/?$', 'get_user_profile'),
)
