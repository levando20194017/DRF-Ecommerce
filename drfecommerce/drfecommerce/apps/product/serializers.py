from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    catalog_name = serializers.CharField(source='catalog.name', read_only=True)
    promotion_name = serializers.CharField(source='promotion.name', read_only=True)
    promotion_id = serializers.CharField(source='promotion.id', read_only=True)
    promotion_from_date = serializers.DateField(source='promotion.from_date', read_only=True)
    promotion_to_date = serializers.DateField(source='promotion.to_date', read_only=True)
    promotion_discount_value = serializers.CharField(source='promotion.discount_value', read_only=True)
    promotion_discount_type = serializers.CharField(source='promotion.discount_type', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
        
class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'