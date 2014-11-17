from django.conf.urls import *

photos = patterns('my.views',
    (r'^$', 'list_photos'),
    (r'^album/(?P<id_album>[0-9]*)/?$', 'list_photos'),
    (r'^orig/(?P<id>[0-9]*)/?$', 'get_photo'),
    (r'^view/(?P<id>[0-9]*)/?$', 'view_photo'),
    (r'^add/?$', 'add_photo'),
    (r'^edit/(?P<id>[0-9]*)/?$', 'edit_photo'),
    (r'^del/(?P<id>[0-9]*)/?$', 'delete_photo'),
)

