from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class News(models.Model):
    class Meta:
        db_table = 'mynews_news'
    author = models.ForeignKey(User, null=True, blank=True, verbose_name=_('user'))
    content = models.TextField(verbose_name=_('content'))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
