from django.db import models
from drfecommerce.apps.store.models import Store
from drfecommerce.apps.product.models import Product
from django.utils import timezone

class ProductStore(models.Model):
    id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.PROTECT, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.IntegerField()

