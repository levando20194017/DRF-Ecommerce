from django.db import models
from django.utils import timezone

class Promotion(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    code = models.CharField(max_length=50, unique=True)
    from_date = models.DateField()
    to_date = models.DateField()
    discount_value = models.FloatField()
    discount_type = models.CharField(
            max_length=50,
            choices=[
            ('percentage', 'Percentage Discount'),
            ('fixed', 'Fixed Discount'),
        ],
            default='percentage'
        )
    status = models.CharField(
            max_length=50,
            choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('expired', 'Expired'),
        ],
            default='active'
        )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'promotions'