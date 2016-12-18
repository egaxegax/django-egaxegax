from django.conf.urls import *

urlpatterns = patterns('books.views',
    (r'^$', 'list_books'),
    (r'^read/(?P<ind>[0-9]*)/(?P<part>.*)/?$', 'read_book'),
    (r'^get_file/(?P<ind>[0-9]*)/?$', 'get_file'),
    (r'^wrt/i/(?P<ind_wrt>[0-9]*)/?$', 'list_wrt'),
    (r'^wrt/?$', 'list_wrt'),
    (r'^wrt/(?P<id_wrt>[0-9]*)/?$', 'list_books'),
    (r'^subj/(?P<id_subj>[0-9]*)/?$', 'list_books'),
    (r'^add/?$', 'add_book'),
    (r'^del/(?P<id>[0-9]*)/?$', 'delete_book'),
    (r'^edit/(?P<id>[0-9]*)/?$', 'edit_book'),
    (r'^user/(?P<id>[0-9]*)/?$', 'get_user_profile'),
)
