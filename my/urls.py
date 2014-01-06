from django.conf.urls.defaults import *

photos = patterns('my.views',
    (r'^$', 'list_photos'),
    (r'^(?P<id>[0-9]*)/?$', 'list_photos'),
    (r'^orig/(?P<id>[0-9]*)/?$', 'get_photo'),
    (r'^add/?$', 'add_photo'),
    (r'^del/(?P<id>[0-9]*)/?$', 'delete_photo'),
)

