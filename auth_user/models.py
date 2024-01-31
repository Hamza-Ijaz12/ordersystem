from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    public_key_file = models.FileField(upload_to='public_keys/')
    private_key_file = models.FileField(upload_to='private_keys/')


    