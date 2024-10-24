from django.db import models
from drfecommerce.apps.store.models import Store
from drfecommerce.apps.product.models import Product
from django.utils import timezone

class ProductStore(models.Model):
    id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.PROTECT, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    quantity_in = models.IntegerField(default=0) # số lượng nhập vào
    remaining_stock = models.IntegerField(default=0)  # Số lượng còn lại trong kho
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'product_store'

