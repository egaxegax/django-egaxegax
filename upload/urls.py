from django.conf.urls import *

urlpatterns = patterns('upload.views',
    (r'^$', 'upload_handler'),
    (r'(?P<pk>\d+)', 'download_handler'),
)