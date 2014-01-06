from django.conf.urls.defaults import *

urlpatterns = patterns('songs.views',
    (r'^$', 'list_songs'),
    (r'^art/i/(?P<ind_art>[0-9]*)/?$', 'list_songs'),
    (r'^art/(?P<id_art>[0-9]*)/?$', 'list_songs'),
    (r'^(?P<id>[0-9]*)/?$', 'get_song'),
    (r'^audio/(?P<id>[0-9]*)/?$', 'get_song_file'),
    (r'^add/?$', 'add_song'),
    (r'^del/(?P<id>[0-9]*)/?$', 'delete_song'),
    (r'^edit/(?P<id>[0-9]*)/?$', 'edit_song'),
    (r'^editaudio/(?P<id>[0-9]*)/?$', 'edit_song_file'),
    (r'^user/(?P<id>[0-9]*)/?$', 'get_user_profile'),
)
