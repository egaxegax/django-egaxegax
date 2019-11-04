from django.conf.urls import include, url
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import RedirectView
#from django.contrib import admin
#admin.autodiscover()

#handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = [
    url(r'^$', include('news.urls')),
    url(r'^about/', 'fotos.views.index'),
    url(r'^av/(?P<id>[0-9]*)/?$', 'fotos.views.get_avatar'),
    url(r'^news/', include('news.urls')),
    url(r'^guestbook$', RedirectView.as_view(url='/posts/')), # old name
    url(r'^guestbook/(?P<p>.*)', RedirectView.as_view(url='/posts/%(p)s')),
    url(r'^posts/', include('posts.urls')),
    url(r'^photos/', include('fotos.urls')),
    url(r'^songs/', include('songs.urls')),
    url(r'^books/', include('books.urls')),
#    url(r'^upload/', include('upload.urls')),
#    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/new/?$', 'fotos.views.create_new_user'),
    url(r'^accounts/login/?$', 'django.contrib.auth.views.login',
        {'authentication_form': AuthenticationForm,
        'template_name': 'login.html',}),
    url(r'^accounts/logout/?$', 'django.contrib.auth.views.logout',
        {'redirect_field_name': 'b',}),
    url(r'^captcha/', include('captcha.urls')),
]
