from django.db import models
from drfecommerce.apps.guest.models import Guest
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('review_reply', 'Review Reply'),
        ('order_update', 'Order Update'),
        ('general', 'General Notification'),
        # Thêm các loại thông báo khác
    )

    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)  # Người nhận thông báo
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)  # Loại thông báo
    message = models.TextField()  # Nội dung thông báo
    related_object_id = models.IntegerField(null=True, blank=True)  # ID của đối tượng liên quan (Review, Order, v.v.)
    is_read = models.BooleanField(default=False)  # Trạng thái đã đọc hay chưa
    created_at = models.DateTimeField(default=timezone.now)  # Thời gian tạo thông báo
    url = models.TextField(null=True, blank=True)  # URL dẫn đến chi tiết liên quan của thông báo
    attachment_url = models.TextField(null=True, blank=True)  # Link đến file đính kèm (nếu có) ví dụ như hình ảnh
    
    class Meta:
        db_table = 'notifications'
        
    def __str__(self):
        return f'Notification for {self.guest} - {self.notification_type}'