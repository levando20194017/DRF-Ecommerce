from django.db import models
from django.utils import timezone

class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    question = models.TextField(max_length=1000)
    is_advised = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'contacts'
     