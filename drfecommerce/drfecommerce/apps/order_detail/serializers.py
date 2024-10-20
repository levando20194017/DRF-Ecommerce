from rest_framework import serializers
from .models import OrderDetail

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['id', 'order', 'product', 'store', 'product_code', 
                  'product_name', 'quantity', 'unit_price', 
                  'location_pickup', 'created_at', 'updated_at']
