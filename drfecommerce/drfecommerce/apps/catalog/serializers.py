from rest_framework import serializers
from .models import Catalog

class serializerGetCatalog(serializers.ModelSerializer):
    class Meta:
        model = Catalog
        fields  = '__all__'

class serializerCreateCatalog(serializers.ModelSerializer):
    class Meta:
        model = Catalog
        fields  = ['name', 'description', 'parent_id', 'level', 'image']