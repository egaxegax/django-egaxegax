from django.conf.urls import include, url
from django.contrib.auth.forms import AuthenticationForm

from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = [
    url(r'^$', include('mynews.urls')),
    url(r'^about/', 'my.views.index'),
    url(r'^av/(?P<id>[0-9]*)/?$', 'my.views.get_avatar'),
    url(r'^news/', include('mynews.urls')),
    url(r'^guestbook$', RedirectView.as_view(url='/posts/')), # old name
    url(r'^guestbook/(?P<p>.*)', RedirectView.as_view(url='/posts/%(p)s')),
    url(r'^posts/', include('posts.urls')),
    url(r'^photos/', include('my.urls')),
    url(r'^songs/', include('songs.urls')),
    url(r'^books/', include('books.urls')),
    url(r'^upload/', include('upload.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/new/?$', 'my.views.create_new_user'),
    url(r'^accounts/login/?$', 'django.contrib.auth.views.login',
        {'authentication_form': AuthenticationForm,
        'template_name': 'login.html',}),
    url(r'^accounts/logout/?$', 'django.contrib.auth.views.logout',
        {'redirect_field_name': 'b',}),
    url(r'^captcha/', include('captcha.urls')),
]
