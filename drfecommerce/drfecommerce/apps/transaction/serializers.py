from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'order', 'order_date', 'transaction_number', 'amount', 
                  'bank_code', 'bank_status', 'bank_message', 'created_at']
