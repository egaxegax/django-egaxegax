from django.contrib import admin
from mynews.models import *

class MsgAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'content', 'date']
    list_per_page = 10
    ordering = ['date']

admin.site.register(News, MsgAdmin)

