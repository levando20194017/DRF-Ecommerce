from rest_framework import serializers
from .models import ProductStore


class ProductStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStore
        fields = '__all__'