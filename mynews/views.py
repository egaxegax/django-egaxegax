#-*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from mynews.forms import *
from mynews.models import *
import time

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

def ClearNewsCache():
    cache.delete_many(['news'])

# Controllers

def list_msg(request, **kw):
    if kw.has_key('all'):
        msg_list = News.objects.order_by('-date')
    else:
        msg_list = cache.get('news')
        if msg_list is None: 
            msg_list = News.objects.order_by('-date')[:4]
            cache.add('news', msg_list)
    return direct_to_template(request, 'mynews.html',
                              {'news': PageList(request, msg_list),
                               'list_all': kw.has_key('all'),
                               'form': AddMsgForm(),
                               'logback': reverse('mynews.views.list_msg')})

# Form actions

def add_msg(request):
    if request.method == 'POST':
        form = AddMsgForm(request.POST)       
        if form.is_valid():
            msg = form.save(commit=False)
            if request.user.is_authenticated():
                msg.author = request.user
            msg.save()
            ClearNewsCache()
    return HttpResponseRedirect(reverse('mynews.views.list_msg'))

def edit_msg(request, **kw):
    id_msg = ZI(kw.get('id'))
    msg = get_object_or_404(News, id=id_msg)
    if request.method == 'POST':
        form = AddMsgForm(request.POST, instance=msg)
        if form.is_valid():
            msg = form.save(commit=False) 
            msg.save(force_update=True)
            ClearNewsCache()
            return HttpResponseRedirect(reverse('mynews.views.list_msg'))
    else:
        form = AddMsgForm(initial={
                                  'id': msg.id,
                                  'content': msg.content}) 
    return direct_to_template(request, 'edit_msg.html',
                              {'form': form})    

def delete_msg(request, **kw):
    if request.user.is_authenticated():
        msg = get_object_or_404(News, id=ZI(kw.get('id')))         
        if not msg.author or request.user.username == msg.author.username:
            msg.delete()
            ClearNewsCache()
    return HttpResponseRedirect(reverse('mynews.views.list_msg'))

def get_user_profile(request, **kw):
    if request.method == 'GET':
        user = get_object_or_404(User, id=ZI(kw.get('id')))
        m = News.objects.filter(author__id=user.id)
        return direct_to_template(request, 'get_user_profile.html',
                                  {'record': m[0],
                                   'record_count': m.count(),
                                   'logback': reverse('mynews.views.list_msg')})