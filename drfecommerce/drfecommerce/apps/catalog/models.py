from django.db import models
from django.utils import timezone

class Catalog(models.Model):
    id = models.AutoField(primary_key=True)  # Integer tự động tăng
    name = models.CharField(max_length=255)  # Tương đương với varchar
    description = models.TextField()  # Tương đương với text
    parent_id = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)  # Khóa ngoại tới chính nó
    level = models.IntegerField()  # Integer
    sort_order = models.FloatField(null=True, blank=True)  # Float
    image = models.CharField(max_length=255, null=True, blank=True)  # Tương đương với varchar
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)  # Tương đương với timestamp
    delete_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        db_table = 'catalogs'  # Tên bảng trong cơ sở dữ liệu

    def __str__(self):
        return self.name