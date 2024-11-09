from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='guest.last_name', read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'guest','guest_name', 'total_cost', 'order_status', 'order_date', 
                  'payment_method', 'payment_status', 'gst_amount', 'shipping_cost', 
                  'shipping_address', 'recipient_phone', 'recipient_name', 
                  'created_at', 'updated_at']
