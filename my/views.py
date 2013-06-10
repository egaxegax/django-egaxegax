#-*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import login
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
import filetransfers.api

art_index = {
    20:'a',21:'b',22:'c',23:'d',24:'e',25:'f',26:'g',27:'h',28:'i',29:'j',30:'k',31:'l',32:'m',33:'n',34:'o',35:'p',36:'q',37:'r',38:'s',39:'t',40:'u',41:'v',42:'w',43:'x',44:'y',45:'z',
    50:u'а',51:u'б',52:u'в',53:u'г',54:u'д',55:u'е',56:u'ё',57:u'ж',58:u'з',59:u'и',60:u'к',61:u'л',62:u'м',63:u'н',64:u'о',65:u'п',66:u'р',67:u'с',68:u'т',69:u'у',70:u'ф',71:u'х',72:u'ц',73:u'ч',74:u'ш',75:u'щ',76:u'э',77:u'ю',78:u'я'
}

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
    
def ClearSongCache():
    cache.delete_many(['songs', 'songs_art'])
    for i in art_index.keys():
        cache.delete_many(['songs_art_i_%s' % (i,)])

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
                              {'photos': PageList(request, photos_list, 7),
                               'view':  view,
                               'logback': reverse('my.views.list_photos')})

def list_songs(request, **kw):
    song_art_count = 0
    art_song_count = 0
    song_last_count = 0
    cache_by_art = False
    per_page = 1000
    if kw.get('id_art'):  # filter by art
        song_list = Song.objects.filter(id=ZI(kw.get('id_art')))
        if song_list.count(): # count songs
            song_list = Song.objects.filter(artist=song_list[0].artist)
            song_art_count = len(song_list)
            per_page = 10
    elif 'id_art' in kw:  # full list
        song_list = cache.get('songs_art')
        if song_list is None:
            song_list = Song.objects.order_by('artist')
            cache_by_art = 'songs_art'
        art_song_count = len(song_list)
    elif kw.get('ind_art'):  # by index
        i = ZI(kw.get('ind_art'))
        lt = art_index.get(i)
        if lt:
            song_list = cache.get('songs_art_i_%s' % (i,))
            if song_list is None:
                song_list = Song.objects.filter(artist__startswith=lt.capitalize()).order_by('artist')
                cache_by_art = 'songs_art_i_%s' % (i,)
        else:
            song_list = Song.objects.none()
        art_song_count = len(song_list)
    else:  # last update
        song_list = cache.get('songs')
        if song_list is None:
            song_list = Song.objects.order_by('-date')[:7]
            cache.add('songs', song_list)
        song_last_count = len(song_list)
    if art_song_count:
        if cache_by_art:  # regroup by art    
            a = []
            art_song_list = []
            for song in song_list:
                if song.artist not in a:
                    a.append(song.artist)
                    art_song_list.append({'id': song.id, 'artist': song.artist, 'count': 1})
                else:
                    art_song_list[len(art_song_list)-1]['count'] += 1
            art_song_count = len(art_song_list)
            song_list = art_song_list        
            cache.add(cache_by_art, song_list)
        for art in song_list:  # sum song by art
            song_art_count += art['count']
    return direct_to_template(request, 'songs.html',
                              {'art_index': art_index,
                               'song_count': song_art_count,
                               'art_count': art_song_count,
                               'last_count': song_last_count,
                               'songs': PageList(request, song_list, per_page),                              
                               'logback': reverse('my.views.list_songs')})

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

def get_avatar(request):
    user_id = ZI(request.session.get('_auth_user_id'))
    profile = get_object_or_404(Profile, user__exact=user_id)
#        blob_key = str(greeting.avatar.file.blobstore_info._BlobInfo__key) 
    return serve_file(request, profile.avatar)

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

def add_song(request):
    if request.method == 'POST':
        form = AddSongForm(request.POST)
        if form.is_valid():
            song = form.save(commit=False)
            song.artist = song.artist.capitalize()
            song.content = song.content.strip('\r\n')
            song.author = request.user
            song.save()
            ClearSongCache()
            return HttpResponseRedirect(reverse('my.views.list_songs'))
    else:
        form = AddSongForm()
    return direct_to_template(request, 'add_song.html',
                              {'form': form})

def delete_song(request, **kw):
    if request.user.is_authenticated():
        song = get_object_or_404(Song, id=ZI(kw.get('id')))         
        if not song.author or request.user.username == song.author.username:
            song.delete()
            ClearSongCache()
    return HttpResponseRedirect(reverse('my.views.list_songs'))

def edit_song(request, **kw):
    id_song = ZI(kw.get('id'))
    song = get_object_or_404(Song, id=id_song)
    if request.method == 'POST':
        form = AddSongForm(request.POST, instance=song)
        if form.is_valid():
            song = form.save(commit=False)
            song.artist = song.artist
            song.content = song.content.strip('\r\n')
            song.author = request.user
            song.date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) 
            song.save(force_update=True)
            ClearSongCache()
            return HttpResponseRedirect(reverse('my.views.get_song', kwargs={'id': id_song}))
    else:
        form = AddSongForm(initial={
                           'id': song.id,
                           'artist': song.artist,
                           'title': song.title,
                           'content': song.content})
    return direct_to_template(request, 'edit_song.html',
                              {'form': form})

def edit_song_file(request, **kw):
    id_song = ZI(kw.get('id'))
    song = get_object_or_404(Song, id=id_song)
    if request.method == 'POST':
        form = AddSongFileForm(request.POST, request.FILES, instance=song)
        if form.is_valid():
            song.save(force_update=True)
            ClearSongCache()
            return HttpResponseRedirect(reverse('my.views.get_song', kwargs={'id': id_song}))
    else:
        form = AddSongFileForm(initial={'id': song.id})
    view_url = reverse('my.views.edit_song_file', kwargs={'id': id_song})
    upload_url, upload_data = prepare_upload(request, view_url)
    return direct_to_template(request, 'edit_song_file.html',
                              {'form': form, 
                               'upload_url': upload_url,
                               'upload_data': upload_data})

def get_song(request, **kw):
    if request.method == 'GET':
        song = get_object_or_404(Song, id=ZI(kw.get('id')))
        t = song.content
        t = t.replace('\n','<br/>')
        t = t.replace('\t', '  ')
        t = t.replace(' ', '&nbsp;')
        song.content = t        
        return direct_to_template(request, 'song.html',
                                  {'song': song,
                                   'autoplay': request.GET.get('a', 0)})

def get_song_file(request, **kw):
    if request.method == 'GET':
        song = get_object_or_404(Song, id=ZI(kw.get('id')))
        fname = os.path.basename(song.audio.name)
        response = HttpResponse(song.audio, mimetype='audio/mp3')
        response['Content-Disposition'] = 'attachment; filename="'+ fname +'"'
        #return serve_file(request, song.audio)
        return response
