from django import forms
from django.utils.translation import ugettext as _
from songs.models import *

class AddSongForm(forms.ModelForm):
    class Meta:
        model = Song
        exclude = ['artist', 'author', 'date', 'audio']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class AddSongFileForm(forms.ModelForm):
    class Meta:
        model = Song
        exclude = ['artist', 'title', 'author', 'content', 'date']

class AddArtForm(forms.ModelForm):
    class Meta:
        model = Art
        exclude = ['count']

class SearchForm(forms.Form):
    search = forms.CharField(max_length=100, label=_('Search by title'))
