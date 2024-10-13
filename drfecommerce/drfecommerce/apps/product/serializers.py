from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    catalog_name = serializers.CharField(source='catalog.name', read_only=True)
    promotion_name = serializers.CharField(source='promotion.name', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
