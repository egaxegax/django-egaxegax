from django import forms
import django.contrib.auth.forms as auth_forms
from my.models import *
from django.utils.translation import ugettext as _

class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'thumb_url']
        widgets = {
            'about': forms.Textarea(attrs={'cols': 40, 'rows': 3}),
        }

class AddPhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        exclude = ['author', 'date', 'width', 'height', 'thumb_url']

