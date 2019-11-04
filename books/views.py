#-*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import truncatewords, striptags, slugify
from django.db.models import Q
from google.appengine.api import images
from google.appengine.ext import blobstore
from books.forms import *
from books.models import *
from templatetags.customfilters import *
from filetransfers.api import prepare_upload
from filetransfers.api import serve_file
from math import ceil
import datetime, time, sys, os.path, re
import zlib, zipfile, base64, mimetypes

wrt_index = {
    20:'a',21:'b',22:'c',23:'d',24:'e',25:'f',26:'g',27:'h',28:'i',29:'j',30:'k',31:'l',32:'m',33:'n',34:'o',35:'p',36:'q',37:'r',38:'s',39:'t',40:'u',41:'v',42:'w',43:'x',44:'y',45:'z',
    50:u'а',51:u'б',52:u'в',53:u'г',54:u'д',55:u'е',56:u'ё',57:u'ж',58:u'з',59:u'и',60:u'к',61:u'л',62:u'м',63:u'н',64:u'о',65:u'п',66:u'р',67:u'с',68:u'т',69:u'у',70:u'ф',71:u'х',72:u'ц',73:u'ч',74:u'ш',75:u'щ',76:u'э',77:u'ю',78:u'я'
}

def E_OS(text):
    "Convert To Unicode"
    return text.decode('utf-8')

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

def AddWrtListCache(wrt_key, wrt_list):
    cache_list = []
    i = 0
    for wrt in wrt_list:
        i += 1
        cache_list.append({
           'id': wrt.id,
           'counter': i,
           'writer': {'id': wrt.id, 'writer': wrt.writer, 'count': wrt.count},
           'tr_wrt': to_translit(wrt.writer),
           'count': wrt.count })
    cache.add('wrts:' + wrt_key, str(cache_list))

def AddSubjListCache(subj_key, subj_list):
    cache_list = []
    for subj in subj_list:
        cache_list.append({
           'id': subj.id,
           'subject': subj.subject,
           'tr_subj': to_translit(subj.subject),
           'count': subj.count })
    cache.add('subj:' + subj_key, str(cache_list))

def AddBookCache(book, part, content):
    st = re.findall('(\d+)', part)
    if st: npart = int(st[0])
    else : npart = 0
    cache_book = {
        'id': book.id,
        'writer': {'id': book.writer.id, 'writer': book.writer.writer, 'count': book.writer.count},
        'subject': ((hasattr(book, 'subject') and book.subject) and {'id': book.subject.id, 'subject': book.subject.subject, 'count': book.subject.count}) or {},
        'title': book.title,
        'tr_wrt': to_translit(book.writer.writer),
        'tr_subj': to_translit(book.subject.subject),
        'tr_titl': to_translit(book.title),
        'index': book.index,
        'part': part,
        'npart': npart,
        'prev_npart': npart - 1,
        'next_npart': npart + 1,
        'file': ((hasattr(book, 'file') and book.file) and {'name': book.file.name.rsplit('/')[-1]}) or {},
        'content': E_OS(content),
        'author': ((hasattr(book, 'author') and book.author) and {'id': book.author.id, 'username': book.author.username}) or {},
        'date': book.date }
    cache.add('book:' + str(book.index) + '.' + str(part), str(cache_book))
    return cache_book

def AddBookListCache(mkey, book_list, **kw):
    cache_list = []
    dlist = []
    for book in book_list:
        try:
            book.writer
        except:
            continue
        dkey = book.writer.writer + ' ' + book.title
        if not dkey in dlist: 
            # description content
            content = GetBookContent(book, 'content.opf')
            dlist.append(dkey)
            cache_list.append({
               'id': book.id,
               'counter': (kw.get('page_num', 1)-1) * kw.get('per_page', 0) + (len(cache_list)+1),
               'writer': {'id': book.writer.id, 'writer': book.writer.writer, 'count': book.writer.count},
               'subject': {'id': book.subject.id, 'subject': book.subject.subject, 'count': book.subject.count},
               'title': book.title,
               'tr_wrt': to_translit(book.writer.writer),
               'tr_subj': to_translit(book.subject.subject),
               'tr_titl': to_translit(book.title),
               'content': truncatewords(content, 80),
               'index': book.index,
               'date': book.date })
    cache.add('books:' + str(mkey), str(cache_list))

def AddWrtCache(wrt_id, wrt):
    cache_wrt = {
        'id': wrt.id,
        'writer': wrt.writer,
        'tr_wrt': to_translit(wrt.writer),
        'content': wrt.content,
        'count': wrt.count }
    cache.add('wrt:' + str(wrt_id), str(cache_wrt))
    return cache_wrt

def ClearWrtCache(wrt_key):
    cache.delete_many(['wrt:' + str(wrt_key)])

def ClearWrtListCache(wrt_key):
    try:    cache.delete_many(['wrts:.full_list', 'wrts:' + str(wrt_key)])
    except: pass
    ClearSubjListCache()

def ClearSubjListCache():
    cache.delete_many(['subj:.full_list'])

def ClearBookCache(book_ind):
    for book_part in range(0, 100):
        cache.delete_many(['book:' + str(book_ind) + '.' + str(book_part)])

def ClearBookListWrtCache(wrt_id):
    for page_num in range(1, 101):
        cache.delete_many(['books:' + str(wrt_id) + '.' + str(page_num)])
    for page_num in range(1, 101):
        cache.delete_many(['books:.last_update' + '.' + str(page_num)])
    ClearSubjListCache()

def ClearBookListSubjCache(subj_id):
    for page_num in range(1, 101):
        cache.delete_many(['books:.subj' + str(subj_id) + '.' + str(page_num)])
    for page_num in range(1, 101):
        cache.delete_many(['books:.last_update' + '.' + str(page_num)])
    ClearSubjListCache()

# extract content text, image, cover_image from .epub
def GetBookContent(book, part='0'):
    content = ''
    if ((hasattr(book, 'file') and book.file)):
        name = book.file.name.replace("'","''").rsplit('/')[-1]
        for blob in blobstore.BlobInfo.gql("WHERE filename = '%s'"  % (name,)):
            za = zipfile.ZipFile(blob.open())
            # get content from zip archive by name or num part
            for f in za.namelist():
                mpart = re.findall('(\d+)', f)
                try:
                    ft = za.read(f)
                    if ((part.isdigit() and len(mpart) and int(part) == int(mpart[0])) or (part == f) or (part == '0' and f == 'index.xhtml')) and f.startswith('index') and f.endswith('.xhtml'):
                        try:
                            content = re.findall('<body[^>]*>(.*)</body>', ft, re.M | re.S)[0]
                        except:
                            content = ''
                    elif (part == f) and f.startswith('content.opf'):
                        try:
                            title = re.findall('>(.*)</dc:title>', ft)[0]
                            writer = re.findall('>(.*)</dc:creator>', ft)[0]
                            content = re.findall('<dc:description>(.*)</dc:description>', ft, re.M | re.S)
                            if len(content):
                                content = content[0]
                            else:
                                content = writer + ' ' + title
                        except:
                            content = ''
                    elif ((part == f) or part.startswith('cover')) and (f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png')):
                        content = base64.b64encode(ft)
                except:
                    continue
                if content:
                    break
    return content

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

# increment subject book count
def IncSubjCount(**kw):
    if kw.get('subject'):
        try:
            form = AddSubjForm(instance=Subject.objects.get(subject=kw['subject']))
            subj = form.save(commit=False)
            subj.count += kw.get('count', 1)
            subj.save(force_update=True)
            if subj.count < 1:
                subj.delete()
        except:
            form = AddSubjForm()
            subj = form.save(commit=False)
            subj.subject = kw['subject']
            subj.count = kw.get('count', 1)
            subj.save()
        return subj

# Controllers

def list_wrt(request, **kw):
    wrt_count = 0
    book_count = 0
    per_page = 100
    wrt_list = []
    wrt_key= ''
    if kw.get('ind_wrt'):  # by index
        i = ZI(kw.get('ind_wrt'))
        if wrt_index.has_key(i):
            wrt_key = wrt_index.get(i).capitalize()
            if not cache.has_key('wrts:' + wrt_key):
                wrt_list = Writer.objects.filter(writer__startswith=wrt_key).order_by('writer')
                AddWrtListCache(wrt_key, wrt_list)
            wrt_list = eval(cache.get('wrts:' + wrt_key))
        else:
            wrt_list = Writer.objects.none()
        wrt_count = len(wrt_list)
    else:  # full list
        wrt_key = '.full_list'
        if not cache.has_key('wrts:' + wrt_key):
            wrt_list = Writer.objects.order_by('writer')
            AddWrtListCache(wrt_key, wrt_list)
        wrt_list = eval(cache.get('wrts:' + wrt_key))
        wrt_count = len(wrt_list)
    for wrt in wrt_list:  # sum book by wrt
        book_count += wrt['count']
    return render_to_response('books.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'wrt_index': wrt_index,
                               'wrt_key': wrt_key,
                               'form': SearchForm(initial={'search':request.GET.get('search')}),
                               'book_count': book_count,
                               'wrt_count': wrt_count,
                               'books': PageList(request, wrt_list, per_page),
                               'logback': reverse('books.views.list_wrt')}))

def list_books(request, **kw):
    book_count = 0
    last_count = 0
    search_count = 0
    book_list = []
    subj_list = []
    subject = None
    writer = None
    page_num = ZI(request.GET.get('page', '1'))
    per_page = 10
    page_bottom = (page_num-1)*per_page
    page_top = page_bottom+per_page
    if kw.get('id_wrt'): # filter by wrt
        wrt_id = ZI(kw.get('id_wrt'))
        wrt_key = str(wrt_id) + '.' + str(page_num)
        if not cache.has_key('books:' + wrt_key):
            book_list = Book.objects.filter(Q(writer=wrt_id)).order_by('title')[page_bottom:page_top]
            AddBookListCache(wrt_key, book_list, page_num=page_num, per_page=per_page)
        book_list = eval(cache.get('books:' + wrt_key))
        if len(book_list):
            book_count = book_list[0]['writer']['count']
            if not cache.has_key('books:' + wrt_key):
                book_list = Book.objects.filter(Q(writer=wrt_id)).order_by('title')[page_bottom:page_top]
                AddBookListCache(wrt_key, book_list, page_num=page_num, per_page=per_page)
            book_list = eval(cache.get('books:' + wrt_key))
            if not cache.has_key('wrt:' + str(wrt_id)):
                writer = Writer.objects.filter(Q(id=wrt_id))
                if len(writer):
                    AddWrtCache(wrt_id, writer[0])
            writer = eval(cache.get('wrt:' + str(wrt_id)))
    elif kw.get('id_subj'): # filter by subj
        subj_id = ZI(kw.get('id_subj'))
        subj_key = '.subj' + str(subj_id) + '.' + str(page_num)
        if not cache.has_key('books:' + subj_key):
            book_list = Book.objects.filter(Q(subject=subj_id))[page_bottom:page_top]
            AddBookListCache(subj_key, book_list, page_num=page_num, per_page=per_page)
        book_list = eval(cache.get('books:' + subj_key))
        if len(book_list):
            book_count = book_list[0]['subject']['count']
            subject = book_list[0]['subject']
    elif request.GET.get('search'): # search
        st = request.GET.get('search')
        search_key = '.search' + to_translit(st) + '.' + str(page_num)
        if not cache.has_key('books:' + search_key):
            book_list = Book.objects.filter(Q(title__startswith=st.capitalize()))[page_bottom:page_top]
            AddBookListCache(search_key, book_list, page_num=page_num, per_page=per_page)
        book_list = eval(cache.get('books:' + search_key))
        book_count = len(book_list)
        search_count = book_count
    else:  # last update
        wrt_id = '.last_update'
        wrt_key = str(wrt_id) + '.' + str(page_num)
        per_page = 10
        page_bottom = (page_num-1)*per_page
        page_top = page_bottom+per_page
        if not cache.has_key('books:' + wrt_key):
            book_list = Book.objects.filter().order_by('-date')[page_bottom:page_top]
            AddBookListCache(wrt_key, book_list, page_num=page_num, per_page=per_page)
        book_list = eval(cache.get('books:' + wrt_key))
        book_count = len(book_list)
        last_count = book_count
        # subjects
        subj_key = '.full_list'
        if not cache.has_key('subj:' + subj_key):
            subj_list = Subject.objects.order_by('subject')
            AddSubjListCache(subj_key, subj_list)
        subj_list = eval(cache.get('subj:' + subj_key))
    num_pages = int(ceil(book_count/ float(per_page)))
    return render_to_response('books.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'wrt_index': wrt_index,
                               'form': SearchForm(initial={'search':request.GET.get('search')}),
                               'book_count': book_count,
                               'last_count': last_count,
                               'search_count': search_count,
                               'books': {  # Paginator imitate
                                   'has_previous': page_num > 1,
                                   'has_next': page_num < num_pages,
                                   'previous_page_number': page_num - 1,
                                   'next_page_number': page_num + 1,
                                   'number': page_num,
                                   'per_page': per_page,
                                   'paginator': { 'num_pages': num_pages },
                                   'object_list': book_list
                               },
                               'subject': subject,
                               'writer': writer,
                               'subjects': PageList(request, subj_list, 1000),       
                               'logback': reverse('books.views.list_books')}))

def list_subj(request, **kw):
    subj_key = '.full_list'
    if not cache.has_key('subj:' + subj_key):
        subj_list = Subject.objects.order_by('subject')
        AddSubjListCache(subj_key, subj_list)
    subj_list = eval(cache.get('subj:' + subj_key))
    return render_to_response('subj.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'subjects': PageList(request, subj_list, 1000),       
                               'logback': reverse('books.views.list_books')}))    

def get_book(request, **kw):
    if request.method == 'GET':
        book_ind = kw.get('ind', '')
        part = kw.get('part', '') or '0'
        if not request.user.is_authenticated() and part != '0' and part != 'cover.jpeg':
            part = '0'
        if not cache.has_key('book:' + book_ind + '.' + str(part)):
            book = get_object_or_404(Book, Q(index=ZI(book_ind)))            
            content = GetBookContent(book, part)
            if not content:
                raise Http404
            book = AddBookCache(book, part, content)
        book = eval(cache.get('book:' + book_ind + '.' + str(part)))
        return book

def read_book(request, **kw):
    book = get_book(request, **kw)
    part = book['part']
    if part.endswith('.jpg') or part.endswith('.jpeg') or part.endswith('.png'):
        content_type = mimetypes.guess_type(book['part'])
        data = base64.b64decode(book['content'])
        if part.startswith('cover'):  # resize cover image
            img = images.Image(image_data=data)
            w = kw.get('width', 200)
            h = int( float(img.height) * (w/float(img.width)) )
            img.resize(width=w, height=h)
            img.im_feeling_lucky()
            data = img.execute_transforms(output_encoding=images.JPEG)
        response = HttpResponse(data, content_type)
        return response
    return render_to_response('book.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'wrt_index': wrt_index,
                               'form': SearchForm(initial={'search':request.GET.get('search')}),
                               'book': book,
                               'logback': reverse('books.views.read_book', kwargs={'ind': book['index'], 'part': book['part']}) }))

def get_file(request, **kw):
    book = get_book(request, **kw)
    if 'file' in book:
        name = book['file']['name'].replace("'","''")
        for blob in blobstore.BlobInfo.gql("WHERE filename = '%s'"  % (name,)):
            response = HttpResponse(blob.open(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="' + name + '"'
            return response
    raise Http404

# Form actions

def add_book(request):
    if request.method == 'POST':
        form = AddBookForm(request.POST, request.FILES)
        form_wrt = AddWrtForm(request.POST)
        form_subj = AddSubjForm(request.POST)
        if form.is_valid() and form_wrt.is_valid() and form_subj.is_valid():
            book = form.save(commit=False)
            writer = form_wrt.save(commit=False)
            subject = form_subj.save(commit=False)
            for f in ['file']:
                if f in request.FILES: # check duplicates
                    o = request.FILES[f]
                    for blob in blobstore.BlobInfo.gql("WHERE filename = '%s'"  % (o.name.replace("'","''"),)):
                        if blob.key() != o.blobstore_info.key(): blob.delete()
            if isinstance(request.user, User):
                book.author = request.user
            # uniques
            book.index = abs(zlib.crc32(writer.writer.encode('utf-8') + ' ' + book.title.encode('utf-8')))
            book_list = Book.objects.filter(Q(index=book.index))
            if len(book_list) == 0:
                book.writer = IncWrtCount(writer=writer.writer)
                book.subject = IncSubjCount(subject=subject.subject)
                book.save()
                ClearWrtListCache(book.writer.writer[0].capitalize())
                ClearBookListWrtCache(book.writer.id)
                ClearBookListSubjCache(book.subject.id)
                ClearBookCache(book.index)
                return HttpResponseRedirect(reverse('books.views.list_books'))
            else:
                edit_book(request, id=book_list[0].id)
    else:
        form = AddBookForm()
        form_wrt = AddWrtForm()
        form_subj = AddSubjForm()
    upload_url, upload_data = prepare_upload(request, reverse('books.views.add_book'))
    return render_to_response('add_book.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'form': form,
                               'form_wrt': form_wrt,
                               'form_subj': form_subj,
                               'upload_url': upload_url,
                               'upload_data': upload_data,
                               'focus': form_wrt['writer'].id_for_label}))

def edit_book(request, **kw):
    book_id = ZI(kw.get('id'))
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = AddBookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            mbook = form.save(commit=False)
            if isinstance(request.user, User):
                mbook.author = request.user
            mbook.date = datetime.datetime.today()
            mbook.save(force_update=True)
            ClearBookListWrtCache(mbook.writer.id)
            ClearBookListSubjCache(mbook.subject.id)
            ClearBookCache(mbook.index)
            return HttpResponseRedirect(reverse('books.views.read_book', kwargs={'ind': mbook.index, 'part': 0}))
    else:
        form = AddBookForm(initial={
                           'id': book.id,
                           'title': book.title,
                           'content': book.content })
    upload_url, upload_data = prepare_upload(request, reverse('books.views.edit_book', kwargs={'id': book.id}))
    return render_to_response('edit_book.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'form': form,
                               'upload_url': upload_url,
                               'upload_data': upload_data,
                               'focus': form['content'].id_for_label}))

def edit_wrt(request, **kw):
    wrt_id = ZI(kw.get('id'))
    wrt = get_object_or_404(Writer, id=wrt_id)
    if request.method == 'POST':
        form = AddWrtFormAll(request.POST, instance=wrt)
        if form.is_valid():
            mwrt = form.save(commit=False)
            mwrt.save(force_update=True)
            ClearWrtCache(wrt.id)
            return HttpResponseRedirect(reverse('books.views.list_books', kwargs={'id_wrt': wrt_id}))
    else:
        form = AddWrtFormAll(initial={
                           'id': wrt.id,
                           'writer': wrt.writer,
                           'content': wrt.content,
                           'count': wrt.count })
    return render_to_response('edit_wrt.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'form': form,
                               'focus': form['content'].id_for_label}))
    

def delete_book(request, **kw):
    if request.user.is_authenticated():
        book = get_object_or_404(Book, id=ZI(kw.get('id')))         
        if request.user.is_superuser or (hasattr(book, 'author') and book.author) and request.user.username == book.author.username:
            book_list = Book.objects.filter(index=book.index)
            if len(book_list) == 1:
                IncWrtCount(writer=book.writer.writer, count=-1)
                IncSubjCount(subject=book.subject.subject, count=-1)
#                 ClearWrtListCache(book.writer.writer[0].capitalize())
#                 ClearBookListWrtCache(book.writer.id)
#                 ClearBookListSubjCache(book.subject.id)                
            ClearBookCache(book.index)
            book.delete()
            if hasattr(book, 'file') and book.file:
                name = book.file.name.rsplit('/')[-1].replace("'","''")
                for blob in blobstore.BlobInfo.gql("WHERE filename = '%s'" % (name,)):
                    blob.delete()
    return HttpResponseRedirect(reverse('books.views.list_books'))

def user_profile(request, **kw):
    if request.method == 'GET':
        user = get_object_or_404(User, id=ZI(kw.get('id')))
        m = Book.objects.filter(author__id=user.id)
        return render_to_response('user_profile.html', 
                                  context_instance=RequestContext(request,
                                  {'request': request,
                                   'record': user,
                                   'record_count': m.count(),
                                   'logback': reverse('books.views.list_books')}))
