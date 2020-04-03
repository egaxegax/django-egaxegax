from djangoappengine.settings_base import *

import os

SECRET_KEY = '=r-$b*8hglm+858&9t043hlm6-&6-3d3vfc4((7yd0dbrakhvi'

LANGUAGE_CODE = 'ru'

USE_I18N = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
#    'django.contrib.admin',
    'djangotoolbox',
    'djangoappengine',
    'captcha',
    'filetransfers',
    'markup_deprecated',
    'books',
    'fotos',
    'news',
    'posts',
    'songs',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',    
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

LOGIN_REDIRECT_URL = '/'

PROJECT_ROOT = os.path.dirname(__file__)

STATIC_URL = '/media/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'media')

MEDIA_URL = '/static/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'static')
TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, 'templates'),)

ROOT_URLCONF = 'urls'

DEBUG = False

ALLOWED_HOSTS = '*'
