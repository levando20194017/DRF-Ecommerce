from rest_framework import serializers
from .models import OrderDetail
from drfecommerce.apps.product.serializers import ProductSerializer
# from drfecommerce.apps.order_detail.models import OrderDetail

class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderDetail
        fields = '__all__'
