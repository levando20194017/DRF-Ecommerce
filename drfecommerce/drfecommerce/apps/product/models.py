from django.db import models
from drfecommerce.apps.my_admin.models import MyAdmin
from drfecommerce.apps.catalog.models import Catalog
from drfecommerce.apps.promotion.models import Promotion
from django.utils import timezone

class Product(models.Model):
    # id = models.AutoField(primary_key=True)
    # admin = models.ForeignKey(MyAdmin, on_delete=models.PROTECT, null=True, blank=True)
    # catalog = models.ForeignKey(Catalog, on_delete=models.PROTECT, null=True, blank=True)
    # promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, null=True, blank=True)
    # code = models.CharField(max_length=50, null=True, blank=True)
    # name = models.CharField(max_length=255)
    # short_description = models.CharField(max_length=255)
    # description = models.TextField()
    # product_type = models.TextField()
    # image = models.CharField(max_length=255)
    # price = models.FloatField()
    # member_price = models.FloatField()  #giá thành viên. tức là người thuộc diện được ưu đãi
    # quantity = models.IntegerField()
    # gallery = models.TextField()
    # weight = models.FloatField()
    # diameter = models.FloatField()
    # dimensions = models.CharField(max_length=255)
    # material = models.CharField(max_length=255)
    # label = models.CharField(max_length=255)
    # created_at = models.DateTimeField(default=timezone.now)
    # updated_at = models.DateTimeField(auto_now=True)
    # delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    # Thông tin chung
    id = models.AutoField(primary_key=True)
    admin = models.ForeignKey(MyAdmin, on_delete=models.PROTECT)
    catalog = models.ForeignKey(Catalog, on_delete=models.PROTECT)
    promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    launch_date = models.DateField(null=True, blank=True)  # Thời điểm ra mắt
    short_description = models.CharField(max_length=255,null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=255)
    gallery = models.TextField()
    price = models.IntegerField()
    color = models.CharField(max_length=255, null=True, blank=True)
    product_type = models.CharField(max_length=255)

    # Màn hình
    screen_size = models.DecimalField(max_digits=3, decimal_places=1)  # Kích thước màn hình (6.9 inches)
    screen_technology = models.CharField(max_length=100, null=True, blank=True)  # Công nghệ màn hình (Super Retina XDR OLED)
    resolution = models.CharField(max_length=50, null=True, blank=True)  # Độ phân giải (2868 x 1320 pixels)
    screen_features = models.TextField(null=True, blank=True)  # Tính năng màn hình

    # Camera sau
    main_camera = models.CharField(max_length=255)  # Thông tin về camera chính
    video_recording = models.TextField(null=True, blank=True)  # Thông tin quay video (4K, 1080p, etc.)
    camera_features = models.TextField(null=True, blank=True)  # Tính năng camera

    # Camera trước
    front_camera = models.CharField(max_length=255)  # Camera trước

    # Vi xử lý & đồ họa
    chipset = models.CharField(max_length=100)  # Chipset (Apple A18 Pro)
    gpu = models.CharField(max_length=100)  # GPU (GPU 6 lõi mới)

    # Giao tiếp & kết nối
    network_support = models.CharField(max_length=50,null=True, blank=True)  # Hỗ trợ mạng (5G, etc.)

    # RAM & lưu trữ
    storage_capacity = models.IntegerField()  # Dung lượng bộ nhớ (GB)

    # Kích thước & Trọng lượng
    dimensions = models.CharField(max_length=50)  # Kích thước (163 x 77,6 x 8,25 mm)
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # Trọng lượng (227 grams)

    # Công nghệ & Tiện ích
    version = models.CharField(max_length=50,null=True, blank=True)  # Hệ điều hành (iOS 18)
    security_features = models.TextField(null=True, blank=True)  # Tính năng bảo mật (Face ID)

    # Pin & Công nghệ sạc
    charging = models.CharField(max_length=255, null=True, blank=True)  # Công nghệ sạc (MagSafe, Qi)

    # Kết nối
    wifi = models.CharField(max_length=50, null=True, blank=True)  # Wi-Fi (Wi-Fi 7)
    bluetooth = models.CharField(max_length=50, null=True, blank=True)  # Bluetooth (5.3)
    other_info = models.CharField(max_length=255,null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'products'
