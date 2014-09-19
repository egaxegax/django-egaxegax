from django import forms
from django.utils.translation import ugettext as _
from guestbook.models import *

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
