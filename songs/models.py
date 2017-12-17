from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class Art(models.Model):
    class Meta:
        db_table = 'my_art'
    artist = models.CharField(max_length=50, db_index=True, verbose_name=_('artist'))
    count = models.IntegerField()

class Song(models.Model):
    class Meta:
        unique_together = (('artist', 'title'),) # not working for gae
        db_table = 'my_song'
    artist = models.CharField(max_length=50, db_index=True, verbose_name=_('artist'))
    title = models.CharField(max_length=50, verbose_name=_('title'))
    content = models.TextField(verbose_name=_('content'))
    author = models.ForeignKey(User, null=True, blank=True, verbose_name=_('user'))
    date = models.DateTimeField(null=True, blank=True, verbose_name=_('date'))
