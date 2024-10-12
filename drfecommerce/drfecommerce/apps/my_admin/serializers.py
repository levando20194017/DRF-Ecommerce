from rest_framework import serializers
from .models import MyAdmin

class AdminSerializerGetData(serializers.ModelSerializer):
    id = serializers.IntegerField() 
    class Meta:
        model = MyAdmin
        exclude = ['password']

class AdminRefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True, help_text="The refresh token")
    
class AdminSerializerLogin(serializers.ModelSerializer):
    class Meta:
        model = MyAdmin
        fields = ['email', 'password']