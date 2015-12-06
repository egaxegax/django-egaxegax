from django.conf.urls import *

urlpatterns = patterns('books.views',
    (r'^$', 'list_books'),
    (r'^(?P<ind>[0-9]*)/?$', 'get_book'),
    (r'^wrt/i/(?P<ind_wrt>[0-9]*)/?$', 'list_wrt'),
    (r'^wrt/?$', 'list_wrt'),
    (r'^wrt/(?P<id_wrt>[0-9]*)/?$', 'list_books'),
    (r'^add/?$', 'add_book'),
    (r'^del/(?P<id>[0-9]*)/?$', 'delete_book'),
    (r'^edit/(?P<id>[0-9]*)/?$', 'edit_book'),
    (r'^user/(?P<id>[0-9]*)/?$', 'get_user_profile'),
)
