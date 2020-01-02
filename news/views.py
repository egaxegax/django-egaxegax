#-*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import timesince
from news.forms import *
from news.models import *
import datetime, time

def ZI(s):
    try:
        s=int(s)
        if not s: raise
        else: return s
    except:
        raise Http404

def PageList(request, qst, per_page=5):
    """Return Paginator list from QuerySet QST with count PER_PAGE."""
    paginator = Paginator(qst, per_page)
    try:    # first page
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:    # last page
        return paginator.page(page)
    except (EmptyPage, InvalidPage):
        return paginator.page(paginator.num_pages)

def AddMsgListCache(theme, msg_list):
    cache_list = []
    for msg in msg_list:
        cache_list.append({
           'id': msg.id,
           'content': msg.content,
           'author': (hasattr(msg, 'author') and hasattr(msg.author, 'id') and {'id': msg.author.id, 'username': msg.author.username}) or {},
           'date': msg.date })
    cache.add('news:' + theme, str(cache_list))

def ClearMsgListCache():
    cache.delete_many(['news:.full_list'])

# Controllers

def list_msg(request, **kw):
    per_page = 7
    allkey = '.full_list'
    if not cache.has_key('news:' + allkey):
        msg_list = News.objects.order_by('-date')
        AddMsgListCache(allkey, msg_list)
    msg_list = eval(cache.get('news:' + allkey))
    return render_to_response('news.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'news': PageList(request, msg_list, per_page),
                               'list_all': kw.has_key('all'),
                               'form': AddMsgForm(),
                               'logback': reverse('news.views.list_msg')}))

# Form actions

def add_msg(request):
    if request.method == 'POST':
        form = AddMsgForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            if request.user.is_authenticated():
                ClearMsgListCache()
                msg.author = request.user
                msg.save()
            else:
                allkey = '.full_list'
                cache_list = []
                if cache.has_key('news:' + allkey):
                    cache_list = eval(cache.get('news:' + allkey))
                    msg = {'content': msg.content,
                           'date': datetime.datetime.today()}
                    if cache_list and not cache_list[0].get('author'):
                        cache_list[0] = msg
                    else:
                        cache_list = [msg] + cache_list
                    ClearMsgListCache()   
                    cache.add('news:' + allkey, str(cache_list), 60*60*3) # cache timeout secs            
    return HttpResponseRedirect(reverse('news.views.list_msg'))

def edit_msg(request, **kw):
    id_msg = ZI(kw.get('id'))
    msg = get_object_or_404(News, id=id_msg)
    if request.method == 'POST':
        form = AddMsgForm(request.POST, instance=msg)
        if form.is_valid():
            msg = form.save(commit=False) 
            msg.save(force_update=True)
            ClearMsgListCache()
            return HttpResponseRedirect(reverse('news.views.list_msg'))
    else:
        form = AddMsgForm(initial={'id': msg.id, 'content': msg.content}) 
    return render_to_response('edit_msg.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'form': form,
                               'focus': form['content'].id_for_label}))

def delete_msg(request, **kw):
    if request.user.is_authenticated():
        msg = get_object_or_404(News, id=ZI(kw.get('id')))
        if request.user.is_superuser or hasattr(msg, 'author') and request.user.username == msg.author.username:         
            ClearMsgListCache()
            msg.delete()
    return HttpResponseRedirect(reverse('news.views.list_msg'))

def user_profile(request, **kw):
    if request.method == 'GET':
        user = get_object_or_404(User, id=ZI(kw.get('id')))
        m = News.objects.filter(author__id=user.id)
        return render_to_response('user_profile.html', 
                                  context_instance=RequestContext(request,
                                  {'request': request,
                                   'record': user,
                                   'record_count': m.count(),
                                   'logback': reverse('news.views.list_msg')}))
