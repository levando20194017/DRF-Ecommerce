from django.db import models
from drfecommerce.apps.order.models import Order
from django.utils import timezone

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    order_date = models.DateTimeField()
    transaction_number = models.CharField(max_length=255)
    amount = models.FloatField()
    bank_code = models.CharField(max_length=50)
    bank_status = models.CharField(max_length=50)
    bank_message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'transactions'
