#-*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.db.models import Q
from google.appengine.api import images
from google.appengine.ext import blobstore
from my.forms import *
from my.models import *
from myfilter.templatetags import myfilter
from filetransfers.api import prepare_upload
from filetransfers.api import serve_file
import datetime, re, sys, urllib2, mimetypes
import transliterate

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

def AddAlbumListCache(allkey, photos_list):
    album_list = {}
    for photo in photos_list:
        if not photo.album in album_list:
            album_list[photo.album] = {
               'album_count': 1,     
               'id': photo.id,
               'title': photo.title,
               'album': photo.album,
               'thumb_url': photo.thumb_url,
               'author': (hasattr(photo, 'author') and hasattr(photo.author, 'id') and {'id': photo.author.id, 'username': photo.author.username}) or {},
               'date': photo.date,
               'memberonly': photo.memberonly }
        else:
            album_list[photo.album]['album_count'] += 1
            if photo.date > album_list[photo.album]['date']:
                album_list[photo.album]['title'] = photo.title
                album_list[photo.album]['thumb_url'] = photo.thumb_url
                album_list[photo.album]['date'] = photo.date
                album_list[photo.album]['memberonly'] = photo.memberonly
    cache.add('photos:' + allkey, str(album_list))

def UpdateAlbumListCache(photo):
    cache_id = 'photos:' + '.full_list' 
    if cache.has_key(cache_id):
        album_list = eval(cache.get(cache_id))
        if not album_list.has_key(photo.album):
            album_list[photo.album] = {'album_count': 0}
        album_list[photo.album] = {
           'album_count': album_list[photo.album]['album_count'] + 1,
           'id': photo.id,
           'title': photo.title,
           'album': photo.album,
           'thumb_url': photo.thumb_url,
           'author': (hasattr(photo, 'author') and hasattr(photo.author, 'id') and {'id': photo.author.id, 'username': photo.author.username}) or {},
           'date': photo.date,
           'memberonly': photo.memberonly }
        ClearPhotosFullListCache()
        cache.add(cache_id, str(album_list))

def AddPhotoCache(photo):
    cache_photo = {
        'id': photo.id,
        'title': photo.title,
        'album': photo.album,
        'thumb_url': photo.thumb_url,
        'author': (hasattr(photo, 'author') and hasattr(photo.author, 'id') and {'id': photo.author.id, 'username': photo.author.username}) or {},
        'date': photo.date,
        'memberonly': photo.memberonly }
    cache.add('photo:' + str(photo.id), str(cache_photo))

def AddPhotosListCache(album, photos_list):
    cache_list = []
    for photo in photos_list:
        cache_list.append({
           'id': photo.id,
           'title': photo.title,
           'album': photo.album,
           'thumb_url': photo.thumb_url,
           'author': (hasattr(photo, 'author') and hasattr(photo.author, 'id') and {'id': photo.author.id, 'username': photo.author.username}) or {},
           'date': photo.date,
           'memberonly': photo.memberonly })
    cache.add('photos:' + album, str(cache_list))

def ClearPhotoCache(photo):
    cache.delete_many(['photo:' + str(photo.id)])

def ClearPhotosListCache(album):
    cache.delete_many(['photos:' + album])

def ClearPhotosFullListCache():
    cache.delete_many(['photos:.full_list'])

# Controllers

def get_avatar(request, **kw):
    profile = get_object_or_404(Profile, user__exact=ZI(kw.get('id')))
    if profile.avatar:
        return serve_file(request, profile.avatar)
    else:
        return HttpResponseRedirect('/media/img/anon.png')

def index(request):
    return render_to_response('index.html', 
                              context_instance=RequestContext(request, 
                              {'request': request,
                               'logback': reverse('my.views.index')}))

def list_photos(request, **kw):
    album =''
    if kw.get('id_album'): # filter by album
        rows = 20
        cols = 5
        photos_list = []
        cache_photo_id = 'photo:' + kw.get('id_album', '')
        if not cache.has_key(cache_photo_id):
            mlist = Photo.objects.filter(id=ZI(kw.get('id_album')))
            if mlist.count():
                AddPhotoCache(mlist[0])
        if cache.has_key(cache_photo_id):
            photo = eval(cache.get(cache_photo_id))
            album = photo['album']
            if not cache.has_key('photos:' + album):
                photos_list = Photo.objects.filter(album=album).order_by('-date')
                AddPhotosListCache(album, photos_list)
            photos_list = eval(cache.get('photos:' + album))
    else: # full list by album
        rows = 100
        cols = 2
        photos_list = {}
        allkey = '.full_list'
        if not cache.has_key('photos:' + allkey):
            photos_list = Photo.objects.all().order_by('album')
            AddAlbumListCache(allkey, photos_list)
        photos_list = eval(cache.get('photos:' + allkey)).values()
    return render_to_response('photos.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'photos': PageList(request, photos_list, rows * cols),
                               'photos_count': len(photos_list),
                               'rows_count': range(1, rows * cols + 1, cols),
                               'album': album,
                               'logback': reverse('my.views.list_photos')}))

# Form actions

def create_new_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        form_profile = CreateProfileForm(request.POST, request.FILES)
        if form.is_valid() and form_profile.is_valid():
            user = form.save(commit=False)
            # user must be active for login to work
            user.is_active = True
            user.save()
            profile = form_profile.save(commit=False)
            profile.user = user #User.objects.get(username__exact=request.POST['username'])
            profile.save()
            return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))
    else:
        form = UserCreationForm()
        form_profile = CreateProfileForm()
    view_url = reverse('my.views.create_new_user')
    upload_url, upload_data = prepare_upload(request, view_url)
    return render_to_response('user_create_form.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'form': form, 
                               'form_profile': form_profile,
                               'upload_url': upload_url,
                               'upload_data': upload_data}))

def add_photo(request):
    if request.method == 'POST':
        form = AddPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            try:
                if 'thumb_url' in form.data:
                    photo.thumb_url = form.data['thumb_url']
                if request.FILES.get('img'):
                    blob_key = request.FILES['img'].blobstore_info._BlobInfo__key
                    photo.thumb_url = images.get_serving_url(blob_key)
#                     data = blobstore.BlobReader(blob_key).read()
#                     img = images.Image(image_data=data)
                    o = request.FILES['img']
                    for blob in blobstore.BlobInfo.gql("WHERE filename = '%s'"  % (o.name.replace("'","''"),)):
                        if blob.key() != o.blobstore_info.key() and blob.md5_hash == o.blobstore_info.md5_hash : blob.delete()
                if 'title1' in form.data:
                    photo.title = FromTranslit(form.data['title1'])
                if 'album1' in form.data:
                    photo.album = FromTranslit(form.data['album1'])
                if 'user' in form.data:
                    usr = User.objects.filter(username=form.data['user'])
                    if usr.count():
                        photo.author = usr[0]
                if isinstance(request.user, User):
                    photo.author = request.user
                photo = form.save()
                ClearPhotosListCache(photo.album)
                UpdateAlbumListCache(photo)
                return HttpResponseRedirect(reverse('my.views.list_photos', kwargs={'id_album': photo.id}))
            except:
                pass
    else:
        form = AddPhotoForm()
    view_url = reverse('my.views.add_photo')
    upload_url, upload_data = prepare_upload(request, view_url)
    return render_to_response('add_photo.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'form': form, 
                               'upload_url': upload_url,
                               'upload_data': upload_data,
                               'focus': form['title'].id_for_label}))

def edit_photo(request, **kw):
    id_photo = ZI(kw.get('id'))
    photo = get_object_or_404(Photo, id=id_photo)
    if request.method == 'POST':
        ClearPhotosListCache(photo.album) # clear old
        form = EditPhotoForm(request.POST, instance=photo)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.save(force_update=True)
            ClearPhotoCache(photo)
            ClearPhotosListCache(photo.album)
            ClearPhotosFullListCache()
            return HttpResponseRedirect(reverse('my.views.list_photos', kwargs={'id_album': id_photo}))
    else:
        form = EditPhotoForm(initial={
                             'id': photo.id,
                             'title': photo.title,
                             'author': photo.author,
                             'album': photo.album})
    return render_to_response('edit_photo.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'form': form,
                               'focus': form['title'].id_for_label}))

def delete_photo(request, **kw):
    if request.user.is_authenticated():
        id_photo = ZI(kw.get('id'))
        photo = get_object_or_404(Photo, id=id_photo)
        if request.user.is_superuser or hasattr(photo, 'author') and request.user.username == photo.author.username:
            ClearPhotoCache(photo)
            ClearPhotosListCache(photo.album)
#            ClearPhotosFullListCache()
            photo.delete()
    return HttpResponseRedirect(reverse('my.views.list_photos'))

def get_photo(request, **kw):
    if request.method == 'GET':
        id_photo = ZI(kw.get('id'))
        if not cache.has_key(id_photo):
            photo = get_object_or_404(Photo, id=ZI(kw.get('id')))
            AddPhotoCache(photo)
        photo = eval(cache.get('photo:' + str(id_photo)))        
        thumb_url = myfilter.get_thumb(photo['thumb_url'], '10000')
#         try:
        response = HttpResponseRedirect(thumb_url)
#         name = transliterate.translit(photo['title'], 'ru', reversed=True)
#         response['Content-Disposition'] = 'inline; filename="' + name + '"'
#         except:
#             raise Http404
        return response
