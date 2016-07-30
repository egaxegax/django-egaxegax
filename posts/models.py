from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class Greeting_Subject(models.Model):
    class Meta:
        db_table = 'guestbook_greeting_subject'
    subject = models.CharField(max_length=150, verbose_name=_('subject'))
    count = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_('date'))

class Greeting(models.Model):
    class Meta:
        db_table = 'guestbook_greeting'
    author = models.ForeignKey(User, verbose_name=_('user'))
    subject = models.ForeignKey(Greeting_Subject, null=True, blank=True, verbose_name=_('subject'))
    title = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('title'))
    content = models.TextField(verbose_name=_('content'))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
