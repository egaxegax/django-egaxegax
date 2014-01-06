from django.conf.urls.defaults import *
from django.contrib.auth.forms import AuthenticationForm

from django.contrib import admin
import my.urls

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    (r'^guestbook$', 'django.views.generic.simple.redirect_to', {'url': '/guestbook/', }),
    (r'^guestbook/', include('guestbook.urls')),
    (r'^$', 'my.views.index'),
    (r'^av/', 'my.views.get_avatar'),
    (r'^photos/', include(my.urls.photos)),
    (r'^songs/', include('songs.urls')),
    (r'^upload/', include('upload.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^accounts/create_user/?$', 'my.views.create_new_user'),
    (r'^accounts/login/?$', 'django.contrib.auth.views.login',
        {'authentication_form': AuthenticationForm,
        'template_name': 'login.html',}),
    (r'^accounts/logout/?$', 'django.contrib.auth.views.logout',
        {'redirect_field_name': 'b',}),
)
