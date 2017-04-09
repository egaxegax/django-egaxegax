from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class Writer(models.Model):
    writer = models.CharField(max_length=150, db_index=True, verbose_name=_('writer'))
    count = models.IntegerField()

class Subject(models.Model):
    subject = models.CharField(max_length=150, db_index=True, verbose_name=_('subject'))
    count = models.IntegerField()

class Book(models.Model):
    class Meta:
        unique_together = ('writer', 'title', 'part') # not worked for gae
    writer = models.ForeignKey(Writer)
    title = models.CharField(max_length=150, verbose_name=_('title'))
    subject = models.ForeignKey(Subject, null=True, blank=True)
    index = models.IntegerField(null=True, blank=True) # unique writer, title
    part = models.IntegerField(verbose_name=_('part'))
    content = models.TextField(verbose_name=_('content'))
    author = models.ForeignKey(User, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('date'))
    file = models.FileField(null=True, blank=True, upload_to='files', verbose_name=_('file'))
