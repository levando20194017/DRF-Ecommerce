from django.db import models
from drfecommerce.apps.store.models import Store
from drfecommerce.apps.product.models import Product
from django.utils import timezone

class ProductIncoming(models.Model):
    #liên quan đến sản phẩm nhập về
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)  # Giá nhập vào
    quantity_in = models.IntegerField()  # Số lượng nhập vào
    vat = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # VAT
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Chi phí vận chuyển
    effective_date = models.DateTimeField(auto_now_add=True)  # Ngày nhập
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'product_incomings'

