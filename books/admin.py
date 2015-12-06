from django.contrib import admin
from books.models import *

class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'writer', 'title']
    list_per_page = 10
    ordering = ['title']
    #search_fields = ['title']

admin.site.register(Book, BookAdmin)
