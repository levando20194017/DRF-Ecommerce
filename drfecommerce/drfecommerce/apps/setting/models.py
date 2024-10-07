from django.db import models
from django.utils import timezone

class Setting(models.Model):
    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
