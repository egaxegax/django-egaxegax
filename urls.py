from django.conf.urls import *
from django.contrib.auth.forms import AuthenticationForm

from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    (r'^$', include('mynews.urls')),
    (r'^about/', 'my.views.index'),
    (r'^av/(?P<id>[0-9]*)/?$', 'my.views.get_avatar'),
    (r'^news/', include('mynews.urls')),
    (r'^guestbook$', RedirectView.as_view(url='/posts/')), # old name
    (r'^guestbook/(?P<p>.*)', RedirectView.as_view(url='/posts/%(p)s')),
    (r'^posts/', include('posts.urls')),
    (r'^photos/', include('my.urls')),
    (r'^songs/', include('songs.urls')),
    (r'^books/', include('books.urls')),
    (r'^upload/', include('upload.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^accounts/create_user/?$', 'my.views.create_new_user'),
    (r'^accounts/login/?$', 'django.contrib.auth.views.login',
        {'authentication_form': AuthenticationForm,
        'template_name': 'login.html',}),
    (r'^accounts/logout/?$', 'django.contrib.auth.views.logout',
        {'redirect_field_name': 'b',}),
    (r'^captcha/', include('captcha.urls')),
)
