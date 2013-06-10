from django.conf.urls.defaults import *

urlpatterns = patterns('guestbook.views',
    (r'^$', 'list_greetings'),
    (r'^(?P<id>[0-9]*)/?$', 'list_greetings'),
    (r'^subj/?$', 'list_subjects'),
    (r'^subj/(?P<id_subj>[0-9]*)/?$', 'list_greetings'),
    (r'^add/?$', 'create_greeting'),
    (r'^edit/(?P<id>[0-9]*)/?$', 'edit_greeting'),
    (r'^del/(?P<id>[0-9]*)/?$', 'delete_greeting'),
    (r'^user/(?P<id>[0-9]*)/?$', 'get_user_profile'),
)
