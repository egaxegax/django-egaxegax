from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class Writer(models.Model):
    writer = models.CharField(max_length=50, db_index=True, verbose_name=_('writer'))
    count = models.IntegerField()

class Book(models.Model):
    class Meta:
        unique_together = ('writer', 'title', 'part')
    writer = models.ForeignKey(Writer)
    title = models.CharField(max_length=50, verbose_name=_('title'))
    index = models.IntegerField(null=True, blank=True)
    part = models.IntegerField(verbose_name=_('part'))
    content = models.TextField(verbose_name=_('content'))
    author = models.ForeignKey(User, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('date'))
