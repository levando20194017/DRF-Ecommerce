from django.db import models
from drfecommerce.apps.guest.models import Guest
from django.utils import timezone

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    guest = models.ForeignKey(Guest, on_delete=models.PROTECT, null=True, blank=True)
    transaction_number = models.CharField(max_length=255)
    total_cost = models.FloatField()
    order_date = models.DateTimeField()
    order_status = models.CharField(max_length=50)
    gst_amount = models.FloatField()
    shipping_cost = models.FloatField()
    location_pickup = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
