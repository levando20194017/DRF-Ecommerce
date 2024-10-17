from rest_framework import serializers
from .models import ProductIncoming


class ProductIncomingSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = ProductIncoming
        fields = '__all__'
        
class ProductIncomingDetailSerializer(serializers.ModelSerializer):    
    store_name = serializers.CharField(source='store.name', read_only=True)
    store_phone_number = serializers.CharField(source='store.phone_number', read_only=True)
    store_email = serializers.CharField(source='store.email', read_only=True)
    store_address = serializers.CharField(source='store.address', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = ProductIncoming
        fields = '__all__'