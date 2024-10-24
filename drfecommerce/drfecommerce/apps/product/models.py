from django.db import models
from drfecommerce.apps.my_admin.models import MyAdmin
from drfecommerce.apps.catalog.models import Catalog
from drfecommerce.apps.promotion.models import Promotion
from django.utils import timezone

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.ForeignKey(MyAdmin, on_delete=models.PROTECT, null=True, blank=True)
    catalog = models.ForeignKey(Catalog, on_delete=models.PROTECT, null=True, blank=True)
    promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=255)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    product_type = models.TextField()
    image = models.CharField(max_length=255)
    price = models.FloatField()
    member_price = models.FloatField()  #giá thành viên. tức là người thuộc diện được ưu đãi
    quantity = models.IntegerField()
    gallery = models.TextField()
    weight = models.FloatField()
    diameter = models.FloatField()
    dimensions = models.CharField(max_length=255)
    material = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'products'
