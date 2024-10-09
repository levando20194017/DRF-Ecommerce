from django.db import models
from drfecommerce.apps.order.models import Order
from drfecommerce.apps.product.models import Product
from django.utils import timezone

class OrderDetail(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    product_code = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    product_part_number = models.CharField(max_length=50)
    quantity = models.IntegerField()
    unit_price = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)