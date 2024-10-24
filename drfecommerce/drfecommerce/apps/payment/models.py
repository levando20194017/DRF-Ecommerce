from django.db import models
from drfecommerce.apps.guest.models import Guest
from drfecommerce.apps.order.models import Order
from django.utils import timezone

class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    guest= models.ForeignKey(Guest, on_delete=models.PROTECT, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.IntegerField()
    credential = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'payments'
