from django.db import models
from drfecommerce.apps.my_admin.models import MyAdmin
from drfecommerce.apps.catalog.models import Catalog
from drfecommerce.apps.promotion.models import Promotion
from django.utils import timezone

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.ForeignKey(MyAdmin, on_delete=models.PROTECT, null=True, blank=True)
    catalog = models.ForeignKey(Catalog, on_delete=models.PROTECT, null=True, blank=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.PROTECT, null=True, blank=True)
    sku = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    part_number = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    product_type = models.TextField()
    image = models.CharField(max_length=255)
    price = models.FloatField()
    member_price = models.FloatField()
    quantity = models.IntegerField()
    gallery = models.TextField()
    weight = models.FloatField()
    diameter = models.FloatField()
    dimensions = models.CharField(max_length=255)
    material = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
