from rest_framework import serializers
from .models import ProductStore


class ProductStoreSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = ProductStore
        fields = '__all__'
        
class DetailProductStoreSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    store_phone_number = serializers.CharField(source='store.phone_number', read_only=True)
    store_email = serializers.CharField(source='store.email', read_only=True)
    store_address = serializers.CharField(source='store.address', read_only=True)
    class Meta:
        model = ProductStore
        fields = '__all__'
        
class StoreHasProductSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    store_phone_number = serializers.CharField(source='store.phone_number', read_only=True)
    store_email = serializers.CharField(source='store.email', read_only=True)
    store_address = serializers.CharField(source='store.address', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = ProductStore
        fields = '__all__'