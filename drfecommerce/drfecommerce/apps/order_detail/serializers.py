from rest_framework import serializers
from .models import OrderDetail

class OrderDetailSerializer(serializers.ModelSerializer):
    product_image = serializers.CharField(source='product.image', read_only=True)
    product_gallery = serializers.CharField(source='product.gallery', read_only=True)
    class Meta:
        model = OrderDetail
        fields = ['id', 'order', 'product', 'product_image', 'product_gallery','store', 'product_code', 
                  'product_name', 'quantity', 'unit_price', 
                  'location_pickup', 'created_at', 'updated_at']
