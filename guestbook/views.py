#-*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from guestbook.forms import *
from guestbook.models import *
import time, sys

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

def AddSubjListCache(subj_list):
    cache_list = []
    for subj in subj_list:
        if not subj.count:
            subj.count = Greeting.objects.filter(subject=subj.id).count()
        if not subj.date:
            subj.date = Greeting.objects.filter(subject=subj.id).order_by('-date')[0].date
        cache_list.append({
           'id': subj.id,
           'subject': subj.subject,
           'count': subj.count,
           'date': subj.date.strftime('%Y-%m-%d %H:%M:%S') })
    cache.add('subjects:.full_list', str(cache_list))

def AddPostCache(post):
    cache_post = [{
       'id': post.id,
       'author': (hasattr(post, 'author') and {'id': post.author.id, 'username': post.author.username}) or {},
       'subject': (hasattr(post, 'subject') and post.subject and {'id': post.subject.id, 'subject': post.subject.subject, 'count': post.subject.count}) or {},
       'title': post.title,
       'content': post.content,
       'date': post.date.strftime('%Y-%m-%d %H:%M:%S') }]
    cache.add('post:' + str(post.id), str(cache_post))

def AddPostListCache(subj_id, posts_list):
    cache_list = []
    for post in posts_list:
        cache_list.append({
           'id': post.id,
           'author': (hasattr(post, 'author') and {'id': post.author.id, 'username': post.author.username}) or {},
           'subject': (hasattr(post, 'subject') and post.subject and {'id': post.subject.id, 'subject': post.subject.subject, 'count': post.subject.count}) or {},
           'title': post.title,
           'content': post.content,
           'date': post.date.strftime('%Y-%m-%d %H:%M:%S') })
    cache.add('posts:' + str(subj_id), str(cache_list))

def ClearSubjListCache():
    cache.delete_many(['subjects:.full_list'])

def ClearPostCache(post):
    cache.delete_many(['post:' + str(post.id)])

def ClearPostListCache(subj_id):
    cache.delete_many(['posts:.full_list', 'posts:' + str(subj_id)])

# increment subject count
def IncSubjCount(**kw):
    if kw.get('subject'):
        try:
            form = AddSubjForm(instance=Greeting_Subject.objects.get(subject=kw['subject']))
            subj = form.save(commit=False)
            subj.count += kw.get('count', 1)
            subj.date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
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

def copy_subj(request):
    for subj in Greeting_Subject.objects.all():
        form = AddSubjForm(instance=subj)
        subj = form.save(commit=False)
        subj.count = Greeting.objects.filter(subject=subj.id).count()
        subj.date = Greeting.objects.filter(subject=subj.id).order_by('-date')[0].date
        subj.save(force_update=True)
    ClearSubjListCache()
    return HttpResponse('Done.')

def list_posts(request, **kw):
    initial = {}
    posts_list = []
    if kw.get('id'):
        post_id = kw.get('id', '')
        if not cache.has_key('post:' + post_id):
            posts_list = get_object_or_404(Greeting, id=ZI(post_id))
            AddPostCache(posts_list)
        posts_list = eval(cache.get('post:' + post_id) or [])
        if len(posts_list) and posts_list[0]['subject']:
            initial['subject'] = posts_list[0]['subject']['subject']
        if len(posts_list) and posts_list[0]['title']:
            initial['title'] = posts_list[0]['title']
    elif kw.get('id_subj'):
        subj_id = kw.get('id_subj', '') 
        if not cache.has_key('posts:' + subj_id):
            posts_list = Greeting.objects.filter(subject=ZI(subj_id)).order_by('-date')
            AddPostListCache(subj_id, posts_list)
        posts_list = eval(cache.get('posts:' + subj_id) or [])
        if len(posts_list) and posts_list[0]['subject']:
            initial['subject'] = posts_list[0]['subject']['subject']
    else:
        subj_id = '.full_list' 
        if not cache.has_key('posts:' + subj_id):
            posts_list = Greeting.objects.all().order_by('-date')
            AddPostListCache(subj_id, posts_list)
        posts_list = eval(cache.get('posts:' + subj_id) or [])
    return render_to_response('posts.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'posts': PageList(request, posts_list),
                               'subject': initial,
                               'form': AddPostForm(),
                               'form_subject': AddSubjForm(initial=initial),
                               'logback': reverse('guestbook.views.list_posts')}))

def list_subjects(request):
    per_page = 100
    allkey = '.full_list'
    if not cache.has_key('subjects:' + allkey):
        subj_list = Greeting_Subject.objects.all().order_by('-count')
        AddSubjListCache(subj_list)
    subj_list = eval(cache.get('subjects:' + allkey))
    return render_to_response('subjects.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'subjects': PageList(request, subj_list, per_page),
                               'form': AddPostForm(),
                               'form_subject': AddSubjForm(),
                               'logback': reverse('guestbook.views.list_subjects')}))

# Form actions

def add_post(request):
    if request.method == 'POST':
        form_subject = AddSubjForm(request.POST)
        form = AddPostForm(request.POST)       
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if form_subject.is_valid():
                subject = IncSubjCount(subject=request.POST['subject'])
                post.subject = subject
                ClearSubjListCache()
                ClearPostListCache(subject.id)
            ClearPostListCache('')
            post.save()
    if 'subject' in locals():
        return HttpResponseRedirect(reverse('guestbook.views.list_posts', kwargs={'id_subj': subject.id}))
    return HttpResponseRedirect(reverse('guestbook.views.list_posts'))

def edit_post(request, **kw):
    post_id = ZI(kw.get('id'))
    post = get_object_or_404(Greeting, id=post_id)
    if request.method == 'POST':
        form = AddPostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
#            post.date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
            post.save(force_update=True)
            if post.subject:
                IncSubjCount(subject=post.subject.subject, count=0)
                ClearSubjListCache()
                ClearPostListCache(post.subject.id)
            ClearPostListCache('')
            ClearPostCache(post)
            if post.subject is None:
                return HttpResponseRedirect(reverse('guestbook.views.list_posts'))
            else:
                return HttpResponseRedirect(reverse('guestbook.views.list_posts', kwargs={'id_subj': post.subject.id}))
    else:
        form = AddPostForm(initial={
                          'id': post.id,
                          'subject': post.subject,
                          'title': post.title,
                          'content': post.content}) 
    return render_to_response('edit_post.html', 
                              context_instance=RequestContext(request,
                              {'request': request,
                               'subject': post.subject,
                               'title': post.title,
                               'form': form,
                               'focus': form['content'].id_for_label}))

def delete_post(request, **kw):
    if request.user.is_authenticated():
        post = get_object_or_404(Greeting, id=ZI(kw.get('id')))
        if request.user.is_superuser or hasattr(post, 'author') and request.user.username == post.author.username:
            if hasattr(post, 'subject') and post.subject:
                IncSubjCount(subject=post.subject.subject, count=-1)
                ClearSubjListCache()
                ClearPostListCache(post.subject.id)
            ClearPostListCache('')
            ClearPostCache(post)
            post.delete()
    if 'id_subj' in request.GET:
        return HttpResponseRedirect(reverse('guestbook.views.list_posts', kwargs={'id_subj': ZI(request.GET.get('id_subj'))}))
    return HttpResponseRedirect(reverse('guestbook.views.list_posts'))

def get_user_profile(request, **kw):
    if request.method == 'GET':
        user = get_object_or_404(User, id=ZI(kw.get('id')))
        m = Greeting.objects.filter(author__id=user.id)
        return render_to_response('get_user_profile.html', 
                                  context_instance=RequestContext(request,
                                  {'request': request,
                                   'record': m[0],
                                   'record_count': m.count(),
                                   'logback': reverse('guestbook.views.list_posts')}))
