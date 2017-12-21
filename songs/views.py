#-*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import striptags, truncatewords
from django.db.models import Q
from django.utils import timezone
from songs.forms import *
from songs.models import *
from filetransfers.api import prepare_upload
from filetransfers.api import serve_file
import os.path, datetime, time, sys, re, base64, zlib
import transliterate

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

def AddArtListCache(artkey, art_list):
    cache_list = []
    for i, art in enumerate(art_list):
        cache_list.append({
           'id': art.id,
           'index': i+1,
           'artist': art.artist,
           'count': art.count,
           'ref_id': art.id })
    cache.add('arts:' + artkey, str(cache_list))

def AddSongCache(song):
    s = t = UnpackContent(song)
    if song.title[:5] != 'about':
        t = re.sub(r"(^|\n)>(.*)","\g<1>*#*\g<2>*##*", t)
        t = re.sub(r"(^|\n)!(.*)","\g<1>*_*\g<2>*__*", t)
        t = re.sub(r"<([^>]*)>", ' *#*\g<1>*##* ', t)
        t = t.replace('*#*', '<b>').replace('*##*', '</b>')
        t = t.replace('*_*', '<i>').replace('*__*', '</i>')
        t = t.replace('\t', ' ')
        t = t.replace(' ', '&nbsp;')
        t = t.replace('\n','<br/>')
    cache_song = {
        'id': song.id,
        'artist': song.artist,
        'art_id': GetArtId(song.artist),
        'title': song.title,
        'desc': truncatewords(s, 200),
        'content': t,
        'author': ((hasattr(song, 'author') and song.author) and {'id': song.author.id, 'username': song.author.username}) or {},
        'date': song.date }
    cache.add('song:' + str(song.id), str(cache_song))

def AddSongListCache(mkey, song_list):
    cache_list = []
    i = 0
    for song in song_list:
        if song.date is None: # nulls date first
            cache_list = [{
               'id': song.id,
               'artist': song.artist,
               'content': UnpackContent(song),
               'author': ((hasattr(song, 'author') and song.author) and {'id': song.author.id, 'username': song.author.username}) or {},
               'title': song.title }] + cache_list
        else:
            i += 1
            cache_list.append({
               'id': song.id,
               'index': i,
               'artist': song.artist,
               'art_id': GetArtId(song.artist),
               'title': song.title,
               'date': song.date })
    cache.add('songs:' + mkey, str(cache_list))

def ClearArtListCache(artkey):
    cache.delete_many(['arts:.full_list', 'arts:' + artkey])

def ClearSongCache(song):
    cache.delete_many(['song:' + str(song.id)])

def ClearSongListCache(artist):
    cache.delete_many(['songs:.last_update', 'songs:.about' + artist, 'songs:' + artist])

def GetArtId(artist):
    if not cache.has_key('arts:.art' + artist):
        art_list = Art.objects.filter(artist=artist)
        AddArtListCache('.art' + artist, art_list)
    art_list = eval(cache.get('arts:.art' + artist))
    try:
        return art_list[0]['id']
    except:
        return ''

def GetArtArtist(art_id):
    if not cache.has_key('arts:.id' + str(art_id)):
        art_list = Art.objects.filter(id=art_id)
        AddArtListCache('.id' + str(art_id), art_list)
    art_list = eval(cache.get('arts:.id' + str(art_id)))
    try:
        return art_list[0]['artist']
    except:
        raise Http404

# pack/unpack text
def PackContent(song):
    return "base64,"+base64.b64encode(zlib.compress(song.content.strip('\r\n').encode('1251')))

def UnpackContent(song):
    t = song.content
    if t[:7]=='base64,':
        try:   t = zlib.decompress(base64.b64decode(t[7:])).decode('cp1251')
        except zlib.error, TypeError: pass
    else: # repack
        song.content = PackContent(song)
        song.save(force_update=True)
    return t

# increment art song count
def IncArtCount(**kw):
    if kw.get('artist'):
        try:
            form = AddArtForm(instance=Art.objects.get(artist=kw['artist']))
            art = form.save(commit=False)
            art.count += kw.get('count', 1)
            art.save(force_update=True)
            if art.count < 1:
                ClearArtListCache(art.artist[0].capitalize())
                ClearArtListCache('.id' + str(art.id))
                ClearArtListCache('.art' + art.artist)
                art.delete()
        except:
            form = AddArtForm()
            art = form.save(commit=False)
            art.artist = kw['artist']
            art.count = kw.get('count', 1)
            art.save()
        return art

# Controllers

def copy_art(request):
    arts = []
    art_list = []
    song_list = Song.objects.order_by('artist')
    for song in song_list:
        if song.artist not in arts:
            arts.append(song.artist)
            art_list.append({'artist': song.artist, 'count': 1})
        else:
            art_list[len(art_list)-1]['count'] += 1
    art_list_old = Art.objects.all()
    for art in art_list_old: # delete old
        IncArtCount(artist=art.artist, count=-art.count)
    for art in art_list: # append new
        IncArtCount(**art)
    return HttpResponse('Done.')

def list_art(request, **kw):
    art_count = 0
    song_count = 0
    per_page = 1000
    art_list = []
    art_key = ''
    if kw.get('ind_art'):  # by index
        i = ZI(kw.get('ind_art'))
        if art_index.has_key(i):
            art_key = art_index.get(i).capitalize()
            if not cache.has_key('arts:' + art_key):
                art_list = Art.objects.filter(artist__startswith=art_key).order_by('artist')
                AddArtListCache(art_key, art_list)
            art_list = eval(cache.get('arts:' + art_key))
        else:
            art_list = Art.objects.none()
        art_count = len(art_list)
    else:  # full list
        art_key = '.full_list'
        if not cache.has_key('arts:' + art_key):
            art_list = Art.objects.order_by('artist')
            AddArtListCache(art_key, art_list)
        art_list = eval(cache.get('arts:' + art_key))
        art_count = len(art_list)
    for art in art_list:  # sum song by art
        song_count += art['count']
    return render_to_response('songs.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'art_index': art_index,
                               'art_key': art_key,
                               'form': SearchForm(initial={'search':request.GET.get('search')}),
                               'song_count': song_count,
                               'art_count': art_count,
                               'songs': PageList(request, art_list, per_page),
                               'logback': reverse('songs.views.list_art')}))

def list_songs(request, **kw):
    song_count = 0
    song_last_count = 0
    search_count = 0
    per_page = 100
    song_list = []
    if kw.get('id_art'): # filter by art
        art_id = ZI(kw.get('id_art'))
        artist = GetArtArtist(art_id)
        if not cache.has_key('songs:' + artist):
            song_list = Song.objects.filter(artist=artist).order_by('title')
            AddSongListCache(artist, song_list)
        song_list = eval(cache.get('songs:' + artist))
        song_count = len(song_list)
    elif request.GET.get('search'): # search
        st = request.GET.get('search')
        search_key = '.search' + transliterate.translit(st, 'ru', reversed=True)
        if not cache.has_key('songs:' + search_key):
            song_list = Song.objects.filter(Q(title__startswith=st))
            AddSongListCache(search_key, song_list)
        song_list = eval(cache.get('songs:' + search_key))    
        song_count = len(song_list)
        search_count = song_count
    else:  # last update
        artist = '.last_update'
        if not cache.has_key('songs:' + artist):
            song_list = Song.objects.order_by('-date')[:10]
            AddSongListCache(artist, song_list)
        song_list = eval(cache.get('songs:' + artist))
        song_last_count = len(song_list)
    return render_to_response('songs.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'art_index': art_index,
                               'form': SearchForm(initial={'search':request.GET.get('search')}),
                               'song_count': song_count,
                               'last_count': song_last_count,
                               'search_count': search_count,
                               'songs': PageList(request, song_list, per_page),                              
                               'logback': reverse('songs.views.list_songs')}))

# Form actions

def add_song(request):
    if request.method == 'POST':
        form = AddSongForm(request.POST)
        form_art = AddArtForm(request.POST)
        if form.is_valid():
            song = form.save(commit=False)            
            song_list = Song.objects.filter(Q(artist=request.POST['artist'])&Q(title=song.title))
            if len(song_list) == 0:
                song.content = PackContent(song)
                art = IncArtCount(artist=request.POST['artist'])
                song.artist = art.artist
                if isinstance(request.user, User):
                    song.author = request.user
                if song.title[:5] != 'about':
                    song.date = timezone.now()
                song.save()
                ClearArtListCache(song.artist[0].capitalize())
                ClearSongListCache(song.artist)
                return HttpResponseRedirect(reverse('songs.views.list_songs'))
            else:
                edit_song(request, id=song_list[0].id)
    else:
        form = AddSongForm()
        form_art = AddArtForm()
    return render_to_response('add_song.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'form': form,
                               'form_art': form_art,
                               'focus': form_art['artist'].id_for_label}))

def edit_song(request, **kw):
    song_id = ZI(kw.get('id'))
    song = get_object_or_404(Song, id=song_id)
    if request.method == 'POST':
        form = AddSongForm(request.POST, instance=song)
        if form.is_valid():
            song = form.save(commit=False)
            song.content = PackContent(song)
            if isinstance(request.user, User):
                song.author = request.user
            if song.date is None and song.title[:5] != 'about':
                song.date = datetime.datetime.today()
            song.save(force_update=True)
            ClearSongListCache(song.artist)
            ClearSongCache(song)
            return HttpResponseRedirect(reverse('songs.views.get_song', kwargs={'id': song_id}))
    else:
        form = AddSongForm(initial={
                           'id': song.id,
                           'title': song.title,
                           'date': song.date,
                           'content': UnpackContent(song)})
    return render_to_response('edit_song.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'form': form,
                               'focus': form['content'].id_for_label}))

def delete_song(request, **kw):
    if request.user.is_authenticated():
        song = get_object_or_404(Song, id=ZI(kw.get('id')))         
        if request.user.is_superuser or hasattr(song, 'author') and request.user.username == song.author.username:
            IncArtCount(artist=song.artist, count=-1)
            ClearArtListCache(song.artist[0].capitalize())
            ClearSongListCache(song.artist)
            ClearSongCache(song)
            song.delete()
    return HttpResponseRedirect(reverse('songs.views.list_songs'))

def get_song(request, **kw):
    if request.method == 'GET':
        song_list = []
        song_id = kw.get('id', '')
        if not cache.has_key('song:' + song_id):
            song = get_object_or_404(Song, id=ZI(song_id))
            AddSongCache(song)
        song = eval(cache.get('song:' + song_id))
        #
        if kw.get('title'): # get song text only
            rs = HttpResponse((song['artist'] + ' ' + song['title'] + '\n\n' +
                                  striptags(song['content']
                                            .replace('&nbsp;',' ').replace('<br/>', '\n'))).encode('cp1251')
                                      +'\n\n(source egaxegax.appspot.com)', 
                              content_type='text/plain')
            return rs
        if song['title'] != 'about':
            mkey = '.about' + song['artist']
            if not cache.has_key('songs:' + mkey):
                song_list = Song.objects.filter(Q(title='about')&Q(artist=song['artist']))
                AddSongListCache(mkey, song_list)
            song_list = eval(cache.get('songs:' + mkey))
        song_list.append( song )
        return render_to_response('song.html', 
                                  context_instance=RequestContext(request,
                                  {'request': request,
                                   'art_index': art_index,
                                   'form': SearchForm(initial={'search':request.GET.get('search')}),
                                   'songs': song_list,
                                   'song': song,
                                   'autoplay': request.GET.get('a', 0),
                                   'logback': reverse('songs.views.get_song', kwargs={'id': song_id}) }))

def get_user_profile(request, **kw):
    if request.method == 'GET':
        user = get_object_or_404(User, id=ZI(kw.get('id')))
        m = Song.objects.filter(author__id=user.id)
        return render_to_response('get_user_profile.html', 
                                  context_instance=RequestContext(request,
                                  {'request': request,
                                   'record': m[0],
                                   'record_count': m.count(),
                                   'logback': reverse('songs.views.list_songs')}))
