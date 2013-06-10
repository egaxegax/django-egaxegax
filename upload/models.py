from django.db import models
from django.contrib.auth.models import User

class UploadModel(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d/%H/%M/%S/')