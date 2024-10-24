from django.db import models
from drfecommerce.apps.guest.models import Guest
from django.utils import timezone
from drfecommerce.apps.product.models import Product
from drfecommerce.apps.store.models import Store

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)  # Một người dùng có thể có nhiều giỏ hàng (nếu cần)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f'Cart {self.id} - Guest: {self.guest}'
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # Một giỏ hàng có thể có nhiều sản phẩm
    store = models.ForeignKey(Store, on_delete=models.CASCADE)  # Liên kết với cửa hàng chứa sản phẩm
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)  # Số lượng sản phẩm trong giỏ hàng
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_item'
        
    def __str__(self):
        return f'CartItem {self.id} - Product: {self.product.name} - Quantity: {self.quantity}'