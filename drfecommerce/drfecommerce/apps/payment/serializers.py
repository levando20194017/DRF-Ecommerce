from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'guest', 'order', 'name', 'description', 'credential', 
                  'image', 'created_at', 'updated_at']
