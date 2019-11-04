from django import forms
import django.contrib.auth.forms as auth_forms
from news.models import *
from django.utils.translation import ugettext as _

class AddMsgForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ['author', 'date']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }
