from django import forms
from upload.models import *

class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadModel