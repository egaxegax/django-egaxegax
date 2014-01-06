from django.contrib import admin
from my.models import *

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'about', 'avatar']
    list_per_page = 10
    #ordering = ['user']
    #search_fields = ['user']

class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'album', 'img', 'date', 'width', 'height']
    list_per_page = 10
    ordering = ['date']
    #search_fields = ['author', 'content']

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Photo, PhotoAdmin)
