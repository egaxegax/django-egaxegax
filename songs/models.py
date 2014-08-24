from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class Song(models.Model):
    class Meta:
        unique_together = ("artist", "title")
        db_table = 'my_song'
    artist = models.CharField(max_length=50, db_index=True, verbose_name=_('artist'))
    title = models.CharField(max_length=50, verbose_name=_('title'))
    content = models.TextField(verbose_name=_('content'))
    audio = models.FileField(upload_to='audio', null=True, blank=True, verbose_name=_('audio'))
    author = models.ForeignKey(User, null=True, blank=True, verbose_name=_('user'))
    date = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('date'))

class Art(models.Model):
    class Meta:
        db_table = "my_art"
    artist = models.CharField(max_length=50, db_index=True, unique=True, verbose_name=_('artist'))
    count = models.IntegerField()
    ref_id = models.IntegerField()
