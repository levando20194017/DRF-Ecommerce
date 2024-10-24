from django.db import models
from drfecommerce.apps.blog.models import Blog
from drfecommerce.apps.tag.models import Tag
from django.utils import timezone

class BlogTag(models.Model):
    id = models.AutoField(primary_key=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True, blank=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'blog_tag'