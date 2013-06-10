#-*- coding: utf-8 -*-

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.exceptions import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from guestbook.forms import *
from guestbook.models import *
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

# Controllers

def list_greetings(request, **kw):
    initial = {}  # form initial
    if kw.get('id'):
        greetings_list = Greeting.objects.filter(id=ZI(kw.get('id')))
        initial = {'id': kw.get('id')}
    elif kw.get('id_subj'):
        greetings_list = Greeting.objects.filter(subject=ZI(kw.get('id_subj')))
        initial = {'id_subj': kw.get('id_subj')}
    else:
        greetings_list = Greeting.objects.all()
    if initial:  # initial subject
        if greetings_list.count():
            if greetings_list[0].subject:
                subject = Greeting_Subject.objects.filter(id=initial.get('id_subj') or greetings_list[0].subject.id)
                if subject.count():
                    initial['subject'] = subject[0].subject
    greetings_list = greetings_list.order_by('-date')
    return direct_to_template(request, 'guestbook.html',
                              {'greetings': PageList(request, greetings_list),
                               'subject': initial,
                               'form': CreateGreetingForm(),
                               'form_subject': CreateGreetingSubjectForm(initial=initial),
                               'logback': reverse('guestbook.views.list_greetings')})

def list_subjects(request):
    subjects_list = Greeting_Subject.objects.all().order_by('subject')
    subjects = PageList(request, subjects_list, 7)
    # aggregates: count posts, last update
    for i, o in enumerate(subjects.object_list):
        m = Greeting.objects.filter(subject__id=o.id)
        subjects.object_list[i].greeting_count = m.count()
        if m.count():
            m = m.order_by('-date')
            subjects.object_list[i].updated = m[0].date
            subjects.object_list[i].author = m[0].author
    return direct_to_template(request, 'subjects.html',
                              {'subjects': subjects,
                               'form': CreateGreetingForm(),
                               'form_subject': CreateGreetingSubjectForm(),
                               'logback': reverse('guestbook.views.list_subjects')})

# Form actions

def create_greeting(request):
    if request.method == 'POST':
        form_subject = CreateGreetingSubjectForm(request.POST)
        form = CreateGreetingForm(request.POST)       
        if form.is_valid():
            greeting = form.save(commit=False)
            if form_subject.is_valid():
                try:
                    subject = Greeting_Subject.objects.get(subject=request.POST['subject'])
                except:
                    subject = form_subject.save()
                greeting.subject = subject
            if request.user.is_authenticated():
                greeting.author = request.user
            greeting.save()
    if 'subject' in locals():
        return HttpResponseRedirect(reverse('guestbook.views.list_greetings', kwargs={'id_subj': subject.id}))
    return HttpResponseRedirect(reverse('guestbook.views.list_greetings'))

def edit_greeting(request, **kw):
    id_greeting = ZI(kw.get('id'))
    greeting = get_object_or_404(Greeting, id=id_greeting)
    if request.method == 'POST':
        form = CreateGreetingForm(request.POST, instance=greeting)
        if form.is_valid():
            greeting = form.save(commit=False)
            greeting.author = request.user
            greeting.date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) 
            greeting.save(force_update=True)
            if greeting.subject is None:
                return HttpResponseRedirect(reverse('guestbook.views.list_greetings'))
            else:
                return HttpResponseRedirect(reverse('guestbook.views.list_greetings', kwargs={'id_subj': greeting.subject.id}))
    else:
        form = CreateGreetingForm(initial={
                                  'id': greeting.id,
                                  'subject': greeting.subject,
                                  'content': greeting.content}) 
    return direct_to_template(request, 'edit_greeting.html',
                              {'subject': greeting.subject,
                               'form': form})    

def delete_greeting(request, **kw):
    if request.user.is_authenticated():
        greeting = get_object_or_404(Greeting, id=ZI(kw.get('id')))
        try:
            subject = Greeting_Subject.objects.get(id=greeting.subject.id)
        except:
            subject = False          
        if not greeting.author or request.user.username == greeting.author.username:
            greeting.delete()
            # delete empty subject
            if subject:
                if not Greeting.objects.filter(subject=subject.id).count():
                    subject.delete()
    if 'id_subj' in request.GET:
        return HttpResponseRedirect(reverse('guestbook.views.list_greetings', kwargs={'id_subj': ZI(request.GET.get('id_subj'))}))
    return HttpResponseRedirect(reverse('guestbook.views.list_greetings'))

def get_user_profile(request, **kw):
    if request.method == 'GET':
        user = get_object_or_404(User, id=ZI(kw.get('id')))
        m = Greeting.objects.filter(author__id=user.id)
        return direct_to_template(request, 'get_user_profile.html',
                                  {'greeting': m[0],
                                   'greeting_count': m.count()})
