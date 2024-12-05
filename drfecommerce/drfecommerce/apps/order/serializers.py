from rest_framework import serializers
from .models import Order
from drfecommerce.apps.product.serializers import ProductSerializer
from drfecommerce.apps.order_detail.models import OrderDetail
from drfecommerce.apps.guest.serializers import GuestSerializerGetData

class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderDetail
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    guest = GuestSerializerGetData(read_only=True)
    items = OrderDetailSerializer(many=True, source='orderdetail_set')
    class Meta:
        model = Order
        fields = '__all__'
