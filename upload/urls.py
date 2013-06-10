from django.conf.urls.defaults import *

urlpatterns = patterns('upload.views',
    (r'^$', 'upload_handler'),
    (r'(?P<pk>\d+)', 'download_handler'),
)