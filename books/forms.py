from django import forms
from django.utils.translation import ugettext as _
from books.models import *

class AddBookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ['writer', 'subject', 'author', 'date', 'index', 'index2', 'thumb_url']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20}),
        }

class AddWrtForm(forms.ModelForm):
    class Meta:
        model = Writer
        exclude = ['count']

class AddSubjForm(forms.ModelForm):
    class Meta:
        model = Subject
        exclude = ['count']

class SearchForm(forms.Form):
    search = forms.CharField(max_length=100, label=_('Search by title'))
