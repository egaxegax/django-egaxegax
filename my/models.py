from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class Profile(models.Model):
    user = models.ForeignKey(User, null=True, unique=True, verbose_name=_('user'))
    about = models.TextField(null=True, blank=True, verbose_name=_('comment'))
    avatar = models.FileField(upload_to='img', null=True, blank=True, verbose_name=_('avatar'))

class Photo(models.Model):
    class Meta:
        unique_together = ('title', 'album')
    title = models.CharField(max_length=50, verbose_name=_('title'))
    album = models.CharField(max_length=50, null=True, verbose_name=_('album'))
    img = models.FileField(upload_to='img', verbose_name=_('img'))
    width = models.IntegerField(null=True, verbose_name=_('width'))
    height = models.IntegerField(null=True, verbose_name=_('height'))
    thumb_url = models.CharField(max_length=255, null=True, verbose_name=_('thumb_url'))
    author = models.ForeignKey(User, null=True, blank=True, verbose_name=_('user'))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
