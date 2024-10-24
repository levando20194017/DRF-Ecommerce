from django.db import models
from drfecommerce.apps.store.models import Store
from drfecommerce.apps.product.models import Product
from drfecommerce.apps.order_detail.models import OrderDetail
from django.utils import timezone

class ProductSale(models.Model):
    #liên quan đến sản phẩm đã bán
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    order_detail = models.ForeignKey(OrderDetail, on_delete=models.CASCADE) #để xác nhận được số lượng sản phẩm này đã bán được ở thời điểm nào, bán cho ai
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)  # Giá bán
    quantity_sold = models.IntegerField()  # Số lượng bán
    vat = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # VAT
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Chi phí vận chuyển
    sale_date = models.DateTimeField(auto_now_add=True)  # Ngày bán
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'product_sales'

