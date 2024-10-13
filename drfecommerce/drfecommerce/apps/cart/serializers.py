from rest_framework import serializers
from .models import Cart, CartItem
from drfecommerce.apps.product.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'created_at']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'guest', 'items', 'created_at', 'updated_at']
