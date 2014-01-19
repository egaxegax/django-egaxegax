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
import time, os.path, re

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

def FromTranslit(s):
    r = {'YO':u'Ё', 'A':u'А', 'B':u'Б', 'V':u'В', 'G':u'Г', 'D':u'Д', 'E':u'Е', 'ZH':u'Ж', 'Z':u'З', 'I':u'И', 'J':u'Й', 'K':u'К', 'L':u'Л', 'M':u'М', 'N':u'Н', 'O':u'О', 'P':u'П',
         'R':u'Р', 'S':u'С', 'T':u'Т', 'U':u'У', 'F':u'Ф', 'H':u'Х', 'C':u'Ц', 'CH':u'Ч', 'SH':u'Ш', 'SHCH':u'Щ', '\'\'':u'Ъ', 'Y\'':u'Ы', '\'':u'Ь', 'E\'':u'Э', 'YU':u'Ю', 'YA':u'Я',          
         'yo':u'ё', 'a':u'а', 'b':u'б', 'v':u'в', 'g':u'г', 'd':u'д', 'e':u'е', 'zh':u'ж', 'z':u'з', 'i':u'и', 'j':u'й', 'k':u'к', 'l':u'л', 'm':u'м', 'n':u'н', 'o':u'о', 'p':u'п',
         'r':u'р', 's':u'с', 't':u'т', 'u':u'у', 'f':u'ф', 'h':u'х', 'c':u'ц', 'ch':u'ч', 'sh':u'ш', 'shch':u'щ', '\'\'':u'ъ', 'y\'':u'ы', '\'':u'ь', 'e\'':u'э', 'yu':u'ю', 'ya':u'я'};
    pattern = '|'.join(map(re.escape, sorted(r, key=len, reverse=True)))
    return re.sub(pattern, lambda m: r[m.group()], s)

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
                photo.title = FromTranslit(form.data['title1'])
                photo.album = FromTranslit(form.data['album1'])
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

def edit_photo(request, **kw):
    id_photo = ZI(kw.get('id'))
    photo = get_object_or_404(Photo, id=id_photo)
    if request.method == 'POST':
        form = EditPhotoForm(request.POST, instance=photo)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.save(force_update=True)
            return HttpResponseRedirect(reverse('my.views.list_photos', kwargs={'id': id_photo}))
    else:
        form = EditPhotoForm(initial={
                           'id': photo.id,
                           'title': photo.title,
                           'album': photo.album})
    return direct_to_template(request, 'edit_photo.html',
                              {'form': form,
                               'photo': photo})

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

