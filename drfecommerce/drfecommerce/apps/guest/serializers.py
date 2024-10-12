from rest_framework import serializers
from .models import Guest

class GuestSerializerGetData(serializers.ModelSerializer):
    id = serializers.IntegerField()  # Thêm trường id kiểu UUID vào Serializer
    class Meta:
        model = Guest
        exclude = ['password']

class GuestSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'email', 'password', 'address', 'city', 'country', 'phone_number']
        
class GuestSerializerLogin(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['email', 'password']
        
class GuestRefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True, help_text="The refresh token")

class GuestSerializerChangeInfor(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True, help_text="The refresh token")
    class Meta:
        model = Guest
        exclude = ['id', 'email', 'password', 'avatar', 'is_verified']
        
class GuestSerializerChangePassword(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True, help_text="The refresh token")
    password = serializers.CharField(required=True, help_text="The refresh token")
    
class GuestSerializerChangeAvatar(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['avatar']