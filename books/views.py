#-*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.db.models import Q
from google.appengine.api import images
from google.appengine.ext import blobstore
from books.forms import *
from books.models import *
from filetransfers.api import prepare_upload
from filetransfers.api import serve_file
import time, os.path, sys, zlib

wrt_index = {
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

def AddWrtListCache(wrtkey, wrt_list):
    cache_list = []
    for wrt in wrt_list:
        cache_list.append({
           'id': wrt.id,
           'writer': wrt.writer,
           'count': wrt.count })
    cache.add('wrts:' + wrtkey, str(cache_list))

def AddBookCache(book):
    cache_book = {
        'id': book.id,
        'writer': {'id': book.writer.id, 'writer': book.writer.writer, 'count': book.writer.count},
        'title': book.title,
        'index': book.index,
        'part': book.part,
        'prev_part': book.part - 1,
        'next_part': book.part + 1,
        'content': book.content,
        'author': (hasattr(book, 'author') and {'id': book.author.id, 'username': book.author.username}) or {},
        'date': book.date.strftime('%Y-%m-%d %H:%M:%S') }
    cache.add('book:' + str(book.index) + '.' + str(book.part), str(cache_book))
    return cache_book

def AddBookPartsCache(book_ind, parts):
    cache.add('book:.parts.' + str(book_ind), str(parts))

def AddBookListCache(wrt_id, book_list):
    cache_list = []
    dlist = []
    for book in book_list:
        try:
            book.writer
        except:
            continue
        dkey = book.writer.writer + ' ' + book.title
        if not dkey in dlist: 
            dlist.append(dkey)
            cache_list.append({
               'id': book.id,
               'writer': {'id': book.writer.id, 'writer': book.writer.writer, 'count': book.writer.count},
               'title': book.title,
               'index': book.index,
               'date': book.date.strftime('%Y-%m-%d %H:%M:%S') })
    cache.add('books:' + str(wrt_id), str(cache_list))

def ClearWrtListCache(wrtkey):
    cache.delete_many(['wrts:.full_list', 'wrts:' + wrtkey])

def ClearBookCache(book_ind):
    cache.delete_many(['book:' + str(book_ind), 'book:.parts.' + str(book_ind)])

def ClearBookListCache(wrt_id):
    cache.delete_many(['books:.last_update', 'books:' + str(wrt_id)])

# increment wrt book count
def IncWrtCount(**kw):
    if kw.get('writer'):
        try:
            form = AddWrtForm(instance=Writer.objects.get(writer=kw['writer']))
            wrt = form.save(commit=False)
            wrt.count += kw.get('count', 1)
            wrt.save(force_update=True)
            if wrt.count < 1:
                ClearWrtListCache(wrt.writer[0].capitalize())
                wrt.delete()
        except:
            form = AddWrtForm()
            wrt = form.save(commit=False)
            wrt.writer = kw['writer']
            wrt.count = kw.get('count', 1)
            wrt.save()
        return wrt

# Controllers

def list_wrt(request, **kw):
    wrt_count = 0
    book_count = 0
    per_page = 100
    wrt_list = []
    if kw.get('ind_wrt'):  # by index
        i = ZI(kw.get('ind_wrt'))
        if wrt_index.has_key(i):
            wrtkey = wrt_index.get(i).capitalize()
            if not cache.has_key('wrts:' + wrtkey):
                wrt_list = Writer.objects.filter(writer__startswith=wrtkey).order_by('writer')
                AddWrtListCache(wrtkey, wrt_list)
            wrt_list = eval(cache.get('wrts:' + wrtkey))
        else:
            wrt_list = Writer.objects.none()
        wrt_count = len(wrt_list)
        for wrt in wrt_list:  # sum book by wrt
            book_count += wrt['count']
    else:  # full list
        wrtkey = '.full_list'
        if not cache.has_key('wrts:' + wrtkey):
            wrt_list = Writer.objects.order_by('writer')
            AddWrtListCache(wrtkey, wrt_list)
        wrt_list = eval(cache.get('wrts:' + wrtkey))
        wrt_count = len(wrt_list)
    return render_to_response('books.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'wrt_index': wrt_index,
                               'form': SearchForm(initial={'search':request.GET.get('search')}),
                               'book_count': book_count,
                               'wrt_count': wrt_count,
                               'books': PageList(request, wrt_list, per_page),
                               'logback': reverse('books.views.list_wrt')}))

def list_books(request, **kw):
    book_count = 0
    book_last_count = 0
    search_count = 0
    per_page = 100
    book_list = []
    if kw.get('id_wrt'): # filter by wrt
        wrt_id = ZI(kw.get('id_wrt'))
        if not cache.has_key('books:' + str(wrt_id)):
            book_list = Book.objects.defer('content').filter(Q(writer=wrt_id)&Q(part=0)).order_by('title')
            AddBookListCache(wrt_id, book_list)
        book_list = eval(cache.get('books:' + str(wrt_id)))
        book_count = len(book_list)
    elif request.GET.get('search'): # search
        st = request.GET.get('search')
        book_list = Book.objects.defer('content').filter(Q(title__startswith=st)&Q(part=0))
        book_count = len(book_list)
        search_count = book_count
    else:  # last update
        wrt_id = '.last_update'
        if not cache.has_key('books:' + wrt_id):
            book_list = Book.objects.defer('content').filter(Q(part=0)).order_by('-date')[:7]
            AddBookListCache(wrt_id, book_list)
        book_list = eval(cache.get('books:' + wrt_id))
        book_last_count = len(book_list)
    return render_to_response('books.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'wrt_index': wrt_index,
                               'form': SearchForm(initial={'search':request.GET.get('search')}),
                               'book_count': book_count,
                               'last_count': book_last_count,
                               'search_count': search_count,
                               'books': PageList(request, book_list, per_page),                              
                               'logback': reverse('books.views.list_books')}))

def get_book(request, **kw):
    if request.method == 'GET':
        book_ind = kw.get('ind', '')
        part = kw.get('part', '') or 0
        if not cache.has_key('book:' + book_ind + '.' + str(part)):
            book = get_object_or_404(Book, Q(index=ZI(book_ind))&Q(part=part))
            AddBookCache(book)
        book = eval(cache.get('book:' + book_ind + '.' + str(part)))
        return render_to_response('book.html', 
                                  context_instance=RequestContext(request,
                                  {'request': request,
                                   'book': book,
                                   'logback': reverse('books.views.get_book', kwargs={'ind': book_ind, 'part': part}) }))

# Form actions

def add_book(request):
    if request.method == 'POST':
        form = AddBookForm(request.POST)
        form_wrt = AddWrtForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            writer = form_wrt.save(commit=False)
            book.author = request.user
            book.index = abs(zlib.crc32(writer.writer.encode('utf-8') + ' ' + book.title.encode('utf-8')))
            book_list = Book.objects.filter(index=book.index)
            if len(book_list):
                wrt = book_list[0].writer
            else:
                wrt = IncWrtCount(writer=writer.writer)
            book.writer = wrt
            book.save()
            ClearWrtListCache(wrt.writer[0].capitalize())
            ClearBookListCache(wrt.id)
            ClearBookCache(book.index)
            return HttpResponseRedirect(reverse('books.views.list_books'))
    else:
        form = AddBookForm()
        form_wrt = AddWrtForm()
    return render_to_response('add_book.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'form': form,
                               'form_wrt': form_wrt,
                               'focus': form_wrt['writer'].id_for_label}))

def edit_book(request, **kw):
    book_id = ZI(kw.get('id'))
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = AddBookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            book.author = request.user
            book.date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) 
            book.save(force_update=True)
            ClearBookListCache(book.writer.id)
            ClearBookCache(book.index)
            return HttpResponseRedirect(reverse('books.views.get_book', kwargs={'ind': book.index, 'part': book.part}))
    else:
        form = AddBookForm(initial={
                           'id': book.id,
                           'title': book.title,
                           'part': book.part,
                           'content': book.content })
    return render_to_response('edit_book.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'form': form,
                               'focus': form['title'].id_for_label}))

def delete_book(request, **kw):
    if request.user.is_authenticated():
        book = get_object_or_404(Book, id=ZI(kw.get('id')))         
        if request.user.is_superuser or hasattr(book, 'author') and request.user.username == book.author.username:
            book_list = Book.objects.filter(index=book.index)
            if len(book_list) == 1:
                IncWrtCount(writer=book.writer.writer, count=-1)
                ClearWrtListCache(book.writer.writer[0].capitalize())
                ClearBookListCache(book.writer.id)
            ClearBookCache(book.index)
            book.delete()
    return HttpResponseRedirect(reverse('books.views.list_books'))

def get_user_profile(request, **kw):
    if request.method == 'GET':
        user = get_object_or_404(User, id=ZI(kw.get('id')))
        m = Book.objects.filter(author__id=user.id)
        return render_to_response('get_user_profile.html', 
                                  context_instance=RequestContext(request,
                                  {'request': request,
                                   'record': m[0],
                                   'record_count': m.count(),
                                   'logback': reverse('books.views.list_books')}))
