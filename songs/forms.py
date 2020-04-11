from django import forms
from django.utils.translation import ugettext as _
from songs.models import *

class AddSongForm(forms.ModelForm):
    class Meta:
        model = Song
        exclude = ['artist', 'author']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class AddArtForm(forms.ModelForm):
    class Meta:
        model = Art
        exclude = ['count']

class SearchForm(forms.Form):
    art = forms.CharField(max_length=100, label=_('Search by artist'))
    tit = forms.CharField(max_length=100, label=_('or title'))
