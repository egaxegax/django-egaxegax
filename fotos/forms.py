from django import forms
from captcha.fields import CaptchaField
from django.utils.translation import ugettext as _
from fotos.models import *

class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'thumb_url']
        widgets = {
            'about': forms.Textarea(attrs={'cols': 40, 'rows': 3}),
        }
    captcha = CaptchaField(label=_('captcha'))

class AddPhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        exclude = ['author', 'date', 'thumb_url']
        widgets = {
            'title': forms.TextInput(attrs={'onkeyup': 'document.getElementById(this.id+1).value=toTranslit(this.value);'}),
            'album': forms.TextInput(attrs={'onkeyup': 'document.getElementById(this.id+1).value=toTranslit(this.value);'}),
        }
    title1 = forms.CharField(widget=forms.HiddenInput, required=False)
    album1 = forms.CharField(widget=forms.HiddenInput, required=False)

class EditPhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        exclude = ['thumb_url', 'img']


class AddUserForm(forms.ModelForm):
    class Meta:
        model = User
