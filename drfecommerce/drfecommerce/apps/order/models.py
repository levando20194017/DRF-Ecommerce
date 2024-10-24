from django.db import models
from drfecommerce.apps.guest.models import Guest
from django.utils import timezone

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    guest = models.ForeignKey(Guest, on_delete=models.PROTECT, null=True, blank=True)
    total_cost = models.FloatField()
    order_status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),           # Đơn hàng đang chờ xử lý
            ('confirmed', 'Confirmed'),       # Đơn hàng đã được xác nhận
            ('shipped', 'Shipped'),           # Đơn hàng đã được giao đi
            ('delivered', 'Delivered'),       # Đơn hàng đã giao thành công
            ('cancelled', 'Cancelled'),       # Đơn hàng đã bị hủy
            ('returned', 'Returned')          # Đơn hàng đã trả lại
        ],
        default='pending'
    )
    order_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=50, choices=[('credit_card', 'Credit Card'), ('bank_transfer', 'Bank Transfer'), ('cash_on_delivery', 'Cash on Delivery'), ('e_wallet', 'E-Wallet')], default='cash_on_delivery')
    payment_status = models.CharField(max_length=50, choices=[('unpaid', 'Unpaid'), ('paid', 'Paid'), ('failed', 'Failed')], default='unpaid')
    gst_amount = models.FloatField()
    shipping_cost = models.FloatField()
    shipping_address = models.CharField(max_length=255, default='Unknown Recipient')
    recipient_phone = models.CharField(max_length=20,  default='Unknown phone')
    recipient_name = models.CharField(max_length=100,  default='Unknown name')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'orders'
