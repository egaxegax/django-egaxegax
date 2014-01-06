from django.contrib import admin
from songs.models import *

class SongAdmin(admin.ModelAdmin):
    list_display = ['id', 'artist', 'title', 'content', 'author', 'date']
    list_per_page = 10
    ordering = ['title']
    #search_fields = ['title']

admin.site.register(Song, SongAdmin)
