from rest_framework import serializers
from .models import Blog
from drfecommerce.apps.blog_tag.models import BlogTag

class BlogSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = Blog
        fields = '__all__'
        
class BlogTagSerializer(serializers.ModelSerializer):
    tag_name = serializers.CharField(source='tag.name', read_only=True)
    class Meta:
        model = BlogTag
        fields = '__all__'
