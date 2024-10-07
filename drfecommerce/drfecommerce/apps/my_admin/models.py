from django.db import models
from django.utils import timezone

class MyAdmin(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    azure_ad = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, default='', blank=True)
