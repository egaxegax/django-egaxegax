from django.conf.urls import *

from . import views

urlpatterns = [
    url(r'test/$', views.test, name='captcha-test'),
    url(r'test-modelform/$', views.test_model_form, name='captcha-test-model-form'),
    url(r'test2/$', views.test_custom_error_message, name='captcha-test-custom-error-message'),
    url(r'test3/$', views.test_per_form_format, name='test_per_form_format'),
    url(r'test-non-required/$', views.test_non_required, name='captcha-test-non-required'),
    url(r'', include('captcha.urls')),
]
