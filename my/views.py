#-*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from google.appengine.api import images
from google.appengine.ext import blobstore
from my.forms import *
from my.models import *
from filetransfers.api import prepare_upload
from filetransfers.api import serve_file
import time, os.path

def ZI(s):
    try:
        s=int(s)
        if not s: raise
        else: return s
    except:
        raise Http404

def PageList(request, qst, per_page=5):
    """Return Paginator list."""
    paginator = Paginator(qst, per_page)
    try:    # first page
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:    # last page
        return paginator.page(page)
    except (EmptyPage, InvalidPage):
        return paginator.page(paginator.num_pages) 
    
# Controllers

def index(request):
    return direct_to_template(request, 'index.html',
                              {'logback': reverse('my.views.index')})

def list_photos(request, **kw):
    photos_list = Photo.objects.all().order_by('-date')
    view = []
    if kw.get('id'): 
        view = Photo.objects.filter(id=ZI(kw.get('id')))
    return direct_to_template(request, 'photos.html',
                              {'photos': PageList(request, photos_list, 6),
                               'view':  view,
                               'logback': reverse('my.views.list_photos')})

# Form actions

def create_new_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        form_profile = CreateProfileForm(request.POST, request.FILES)
        if form.is_valid(): # and form_profile.is_valid():
            user = form.save(commit=False)
            # user must be active for login to work
            user.is_active = True
            user.save()
            profile = form_profile.save(commit=False)
            profile.user = User.objects.get(username__exact=request.POST['username'])
            profile.save()
            return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))
    else:
        form = UserCreationForm()
        form_profile = CreateProfileForm()
    view_url = reverse('my.views.create_new_user')
    upload_url, upload_data = prepare_upload(request, view_url)
    return direct_to_template(request, 'user_create_form.html',
                              {'form': form, 
                               'form_profile': form_profile,
                               'upload_url': upload_url,
                               'upload_data': upload_data}) 

def get_avatar(request, **kw):
    profile = get_object_or_404(Profile, user__exact=ZI(kw.get('id')))
    if profile.avatar:
#        blob_key = str(greeting.avatar.file.blobstore_info._BlobInfo__key)
        return serve_file(request, profile.avatar)
    else:
        return HttpResponseRedirect('/media/img/anon.png')

def add_photo(request):
    if request.method == 'POST':
        form = AddPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            blob_key = request.FILES['img'].blobstore_info._BlobInfo__key
            data = blobstore.BlobReader(blob_key).read()
            try:
                img = images.Image(image_data=data)
                photo.width = img.width
                photo.height = img.height
                photo.thumb_url = images.get_serving_url(blob_key)
                photo.author = request.user
                photo = form.save()            
                return HttpResponseRedirect(reverse('my.views.list_photos'))
            except:
                pass
    else:
        form = AddPhotoForm()
    view_url = reverse('my.views.add_photo')
    upload_url, upload_data = prepare_upload(request, view_url)
    return direct_to_template(request, 'add_photo.html',
                              {'form': form, 
                               'upload_url': upload_url,
                               'upload_data': upload_data})

def delete_photo(request, **kw):
    if request.user.is_authenticated():
        photo = get_object_or_404(Photo, id=ZI(kw.get('id')))         
        if not photo.author or request.user.username == photo.author.username:
            photo.delete()
    return HttpResponseRedirect(reverse('my.views.list_photos'))

def get_photo(request, **kw):
    if request.method == 'GET':
        photo = get_object_or_404(Photo, id=ZI(kw.get('id')))
        return serve_file(request, photo.img)

