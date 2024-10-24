from django.db import models
from django.utils import timezone

class Store(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    opening_hours = models.TimeField()
    closing_hours = models.TimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'stores'
