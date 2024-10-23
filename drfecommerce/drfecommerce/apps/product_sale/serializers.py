from rest_framework import serializers
from .models import ProductSale
from drfecommerce.apps.product.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        
class ProductSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSale
        fields = '__all__'
    
class ProductReportSaleSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Liên kết với ProductSerializer

    class Meta:
        model = ProductSale
        fields = ['product', 'sale_price', 'quantity_sold', 'vat', 'shipping_cost', 'sale_date']