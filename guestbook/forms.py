from django import forms
import django.contrib.auth.forms as auth_forms
from guestbook.models import *
from django.utils.translation import ugettext as _

class CreateGreetingForm(forms.ModelForm):
    class Meta:
        model = Greeting
        exclude = ['author', 'subject', 'date']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class CreateGreetingSubjectForm(forms.ModelForm):
    class Meta:
        model = Greeting_Subject
