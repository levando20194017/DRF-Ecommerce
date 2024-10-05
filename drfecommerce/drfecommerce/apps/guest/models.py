from django.db import models
import uuid

class Guest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    address = models.CharField(default= '', max_length=255, null=True, blank=True)
    city = models.CharField(default= '', max_length=255, null=True, blank=True)
    country = models.CharField(default= '', max_length=255, null=True, blank=True)
    postcode = models.CharField(default= '', max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255)
    phone_number = models.CharField(default= '', max_length=20, null=True, blank=True)
    avatar = models.CharField(default= '', max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, default='')
     
    @property
    def is_authenticated(self):
        return True