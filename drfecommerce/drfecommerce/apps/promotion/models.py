from django.db import models
from django.utils import timezone

class Promotion(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    code = models.CharField(max_length=50)
    from_date = models.DateField()
    to_date = models.DateField()
    special_price = models.FloatField()
    member_price = models.FloatField()
    rate = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'promotions'