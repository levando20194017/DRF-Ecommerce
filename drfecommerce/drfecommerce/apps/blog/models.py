from django.db import models
from drfecommerce.apps.my_admin.models import MyAdmin
from drfecommerce.apps.category.models import Category
from django.utils import timezone

class Blog(models.Model):
    id = models.AutoField(primary_key=True)
    my_admin = models.ForeignKey(MyAdmin, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    short_description = models.TextField()
    content = models.TextField()
    status = models.CharField(max_length=50)
    image =  models.CharField(default= '', max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    delete_at = models.DateTimeField(null=True, blank=True, default=None)
    
    class Meta:
        db_table = 'blogs'