from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    guest_last_name = serializers.CharField(source='guest.last_name', read_only=True)
    guest_first_name = serializers.CharField(source='guest.first_name', read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
