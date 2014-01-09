from django import forms
import django.contrib.auth.forms as auth_forms
from songs.models import *
from django.utils.translation import ugettext as _

class AddSongForm(forms.ModelForm):
    class Meta:
        model = Song
        exclude = ['author', 'date', 'audio']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class AddSongFileForm(forms.ModelForm):
    class Meta:
        model = Song
        exclude = ['artist', 'title', 'author', 'content', 'date']

class SearchForm(forms.Form):
    search = forms.CharField(max_length=100, label=_('Search by title'))
