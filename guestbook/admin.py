from django.contrib import admin
from guestbook.models import *

class GreetingAdmin(admin.ModelAdmin):
    #fieldsets = [
    #    ('', {'fields': ['author', 'subject', 'content']})        
    #]
    #readonly_fields = ['id', 'date']
    list_display = ['id', 'author', 'subject', 'content', 'date']
    list_per_page = 10
    ordering = ['date']
    #search_fields = ['author', 'content']

class SubjectAdmin(admin.ModelAdmin):
    #fieldsets = [
    #    ('', {'fields': ['id', 'subject']})        
    #]
    #readonly_fields = ['id']
    list_display = ['id', 'subject']
    list_per_page = 10

admin.site.register(Greeting, GreetingAdmin)
admin.site.register(Greeting_Subject, SubjectAdmin)
