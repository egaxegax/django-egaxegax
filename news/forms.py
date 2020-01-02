from django import forms
from news.models import *

class AddMsgForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ['author', 'date']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5, 'required': True}),
        }
